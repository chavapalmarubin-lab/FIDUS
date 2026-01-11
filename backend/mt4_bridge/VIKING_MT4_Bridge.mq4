//+------------------------------------------------------------------+
//|                                           VIKING_MT4_Bridge.mq4  |
//|                              VIKING Trading Operations MT4 EA    |
//|                         Separate from FIDUS - Account 33627673   |
//+------------------------------------------------------------------+
#property copyright "VIKING Trading Operations"
#property link      ""
#property version   "1.00"
#property strict
#property description "VIKING MT4 Bridge - Syncs account data to MongoDB"
#property description "Port: 8001 | Collection: viking_accounts"

//--- Input parameters
input string   InpEndpoint = "http://localhost:8001/api/viking/sync";  // Sync endpoint URL
input int      InpSyncInterval = 300;  // Sync interval in seconds (5 minutes)
input bool     InpSyncDeals = true;    // Also sync deal history
input int      InpDealsLookback = 30;  // Days of deal history to sync
input bool     InpDebugMode = false;   // Enable debug logging

//--- Global variables
datetime g_lastSyncTime = 0;
datetime g_lastDealSyncTime = 0;
int g_syncCount = 0;
int g_errorCount = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=================================================");
   Print("VIKING MT4 Bridge v1.00 - Initializing...");
   Print("Account: ", AccountNumber());
   Print("Broker: ", AccountCompany());
   Print("Server: ", AccountServer());
   Print("Endpoint: ", InpEndpoint);
   Print("Sync Interval: ", InpSyncInterval, " seconds");
   Print("=================================================");
   
   // Verify this is the correct VIKING account
   if(AccountNumber() != 33627673)
   {
      Print("WARNING: This EA is designed for VIKING account 33627673");
      Print("Current account: ", AccountNumber());
      // Don't prevent loading, just warn
   }
   
   // Initial sync on load
   SyncAccountData();
   
   // Set timer for periodic sync
   EventSetTimer(InpSyncInterval);
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("VIKING MT4 Bridge stopped. Total syncs: ", g_syncCount, ", Errors: ", g_errorCount);
}

//+------------------------------------------------------------------+
//| Timer function - periodic sync                                     |
//+------------------------------------------------------------------+
void OnTimer()
{
   SyncAccountData();
   
   // Sync deals less frequently (every 3rd sync)
   if(InpSyncDeals && g_syncCount % 3 == 0)
   {
      SyncDealHistory();
   }
}

//+------------------------------------------------------------------+
//| Main sync function - sends account data to Python service          |
//+------------------------------------------------------------------+
void SyncAccountData()
{
   string jsonPayload = BuildAccountJSON();
   
   if(InpDebugMode)
   {
      Print("Syncing account data...");
      Print("Payload: ", jsonPayload);
   }
   
   string response = "";
   int result = SendHTTPPost(InpEndpoint, jsonPayload, response);
   
   if(result == 200)
   {
      g_syncCount++;
      g_lastSyncTime = TimeCurrent();
      
      if(InpDebugMode || g_syncCount % 10 == 0)
      {
         Print("✅ VIKING Sync #", g_syncCount, " successful at ", TimeToString(g_lastSyncTime));
      }
   }
   else
   {
      g_errorCount++;
      Print("❌ VIKING Sync failed. HTTP code: ", result, ", Response: ", response);
   }
}

//+------------------------------------------------------------------+
//| Build JSON payload for account data                                |
//+------------------------------------------------------------------+
string BuildAccountJSON()
{
   string json = "{";
   
   // Account identification
   json += "\"account\":" + IntegerToString(AccountNumber()) + ",";
   json += "\"strategy\":\"CORE\",";
   json += "\"broker\":\"" + EscapeJSON(AccountCompany()) + "\",";
   json += "\"server\":\"" + EscapeJSON(AccountServer()) + "\",";
   json += "\"platform\":\"MT4\",";
   
   // Account balances
   json += "\"balance\":" + DoubleToString(AccountBalance(), 2) + ",";
   json += "\"equity\":" + DoubleToString(AccountEquity(), 2) + ",";
   json += "\"margin\":" + DoubleToString(AccountMargin(), 2) + ",";
   json += "\"free_margin\":" + DoubleToString(AccountFreeMargin(), 2) + ",";
   json += "\"profit\":" + DoubleToString(AccountProfit(), 2) + ",";
   
   // Account info
   json += "\"currency\":\"" + AccountCurrency() + "\",";
   json += "\"leverage\":" + IntegerToString(AccountLeverage()) + ",";
   
   // Status
   json += "\"status\":\"active\",";
   json += "\"error_message\":null,";
   
   // Timestamp
   json += "\"sync_timestamp\":\"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\",";
   json += "\"sync_type\":\"account\"";
   
   json += "}";
   
   return json;
}

//+------------------------------------------------------------------+
//| Sync deal history to MongoDB                                       |
//+------------------------------------------------------------------+
void SyncDealHistory()
{
   datetime startTime = TimeCurrent() - InpDealsLookback * 86400;  // Lookback days in seconds
   
   string dealsEndpoint = StringSubstr(InpEndpoint, 0, StringFind(InpEndpoint, "/sync")) + "/deals/batch";
   
   string jsonPayload = BuildDealsJSON(startTime);
   
   if(StringLen(jsonPayload) <= 10)
   {
      if(InpDebugMode) Print("No deals to sync");
      return;
   }
   
   string response = "";
   int result = SendHTTPPost(dealsEndpoint, jsonPayload, response);
   
   if(result == 200)
   {
      g_lastDealSyncTime = TimeCurrent();
      if(InpDebugMode) Print("✅ Deal history synced successfully");
   }
   else
   {
      Print("❌ Deal sync failed. HTTP code: ", result);
   }
}

//+------------------------------------------------------------------+
//| Build JSON payload for deal history                                |
//+------------------------------------------------------------------+
string BuildDealsJSON(datetime startTime)
{
   string json = "[";
   int dealCount = 0;
   
   // Get history for the lookback period
   if(!HistorySelect(startTime, TimeCurrent()))
   {
      Print("Failed to select history");
      return "[]";
   }
   
   int totalOrders = OrdersHistoryTotal();
   
   for(int i = 0; i < totalOrders; i++)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY))
         continue;
      
      // Only include closed trades (not pending orders)
      if(OrderType() > OP_SELL)
         continue;
      
      if(dealCount > 0) json += ",";
      
      json += "{";
      json += "\"account\":" + IntegerToString(AccountNumber()) + ",";
      json += "\"viking_account_id\":\"VIKING_" + IntegerToString(AccountNumber()) + "\",";
      json += "\"strategy\":\"CORE\",";
      json += "\"ticket\":" + IntegerToString(OrderTicket()) + ",";
      json += "\"symbol\":\"" + OrderSymbol() + "\",";
      json += "\"type\":\"" + (OrderType() == OP_BUY ? "buy" : "sell") + "\",";
      json += "\"volume\":" + DoubleToString(OrderLots(), 2) + ",";
      json += "\"open_time\":\"" + TimeToString(OrderOpenTime(), TIME_DATE|TIME_SECONDS) + "\",";
      json += "\"close_time\":\"" + TimeToString(OrderCloseTime(), TIME_DATE|TIME_SECONDS) + "\",";
      json += "\"open_price\":" + DoubleToString(OrderOpenPrice(), 5) + ",";
      json += "\"close_price\":" + DoubleToString(OrderClosePrice(), 5) + ",";
      json += "\"profit\":" + DoubleToString(OrderProfit(), 2) + ",";
      json += "\"commission\":" + DoubleToString(OrderCommission(), 2) + ",";
      json += "\"swap\":" + DoubleToString(OrderSwap(), 2) + ",";
      json += "\"comment\":\"" + EscapeJSON(OrderComment()) + "\"";
      json += "}";
      
      dealCount++;
      
      // Limit batch size to avoid huge payloads
      if(dealCount >= 500) break;
   }
   
   json += "]";
   
   if(InpDebugMode) Print("Built deals JSON with ", dealCount, " trades");
   
   return json;
}

//+------------------------------------------------------------------+
//| Send HTTP POST request                                             |
//+------------------------------------------------------------------+
int SendHTTPPost(string url, string payload, string &response)
{
   char post[];
   char result[];
   string headers = "Content-Type: application/json\r\n";
   
   StringToCharArray(payload, post, 0, WHOLE_ARRAY, CP_UTF8);
   ArrayResize(post, ArraySize(post) - 1);  // Remove null terminator
   
   int timeout = 5000;  // 5 second timeout
   
   ResetLastError();
   
   int res = WebRequest(
      "POST",
      url,
      headers,
      timeout,
      post,
      result,
      headers
   );
   
   if(res == -1)
   {
      int error = GetLastError();
      Print("WebRequest error: ", error);
      
      if(error == 4060)
      {
         Print("ERROR: URL not allowed. Add this URL to MT4 allowed URLs:");
         Print("Tools -> Options -> Expert Advisors -> Allow WebRequest for listed URL:");
         Print(url);
      }
      
      return -1;
   }
   
   response = CharArrayToString(result);
   
   return res;
}

//+------------------------------------------------------------------+
//| Escape special characters for JSON                                 |
//+------------------------------------------------------------------+
string EscapeJSON(string text)
{
   string result = text;
   StringReplace(result, "\\", "\\\\");
   StringReplace(result, "\"", "\\\"");
   StringReplace(result, "\n", "\\n");
   StringReplace(result, "\r", "\\r");
   StringReplace(result, "\t", "\\t");
   return result;
}

//+------------------------------------------------------------------+
//| OnTick - Not used but required                                     |
//+------------------------------------------------------------------+
void OnTick()
{
   // Account sync is timer-based, not tick-based
   // This keeps CPU usage low
}
//+------------------------------------------------------------------+
