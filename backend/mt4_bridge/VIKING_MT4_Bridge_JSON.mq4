//+------------------------------------------------------------------+
//|                                       VIKING_MT4_Bridge_JSON.mq4 |
//|                                         VKNG AI Trading Operations|
//|                              Writes account data to JSON file     |
//+------------------------------------------------------------------+
#property copyright "VKNG AI"
#property link      "https://getvkng.com"
#property version   "2.00"
#property strict

//--- Input parameters
input int      SyncIntervalSeconds = 30;    // Sync interval in seconds
input string   OutputFileName = "viking_account_data.json";  // Output file name

//--- Global variables
datetime lastSyncTime = 0;
int fileHandle = INVALID_HANDLE;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("VIKING MT4 Bridge (JSON) initialized");
   Print("Account: ", AccountNumber());
   Print("Broker: ", AccountCompany());
   Print("Server: ", AccountServer());
   Print("Output file: ", OutputFileName);
   Print("Sync interval: ", SyncIntervalSeconds, " seconds");
   
   // Do initial sync
   SyncAccountData();
   
   // Set timer for periodic sync
   EventSetTimer(SyncIntervalSeconds);
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("VIKING MT4 Bridge (JSON) stopped. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Timer function - called every SyncIntervalSeconds                  |
//+------------------------------------------------------------------+
void OnTimer()
{
   SyncAccountData();
}

//+------------------------------------------------------------------+
//| Tick function - also sync on new ticks for real-time updates      |
//+------------------------------------------------------------------+
void OnTick()
{
   // Sync every 10 seconds on tick as backup
   if(TimeCurrent() - lastSyncTime >= 10)
   {
      SyncAccountData();
   }
}

//+------------------------------------------------------------------+
//| Main sync function - writes account data to JSON file             |
//+------------------------------------------------------------------+
void SyncAccountData()
{
   // Build JSON string
   string json = BuildAccountJSON();
   
   // Write to file
   if(WriteJSONToFile(json))
   {
      lastSyncTime = TimeCurrent();
      Print("VIKING Sync successful - Balance: $", DoubleToString(AccountBalance(), 2), 
            " Equity: $", DoubleToString(AccountEquity(), 2));
   }
   else
   {
      Print("VIKING Sync FAILED - Could not write to file");
   }
}

//+------------------------------------------------------------------+
//| Build JSON string with account data                                |
//+------------------------------------------------------------------+
string BuildAccountJSON()
{
   string json = "{";
   
   // Account info
   json += "\"account\":" + IntegerToString(AccountNumber()) + ",";
   json += "\"strategy\":\"CORE\",";
   json += "\"broker\":\"" + EscapeJSON(AccountCompany()) + "\",";
   json += "\"server\":\"" + EscapeJSON(AccountServer()) + "\",";
   json += "\"platform\":\"MT4\",";
   json += "\"currency\":\"" + AccountCurrency() + "\",";
   
   // Balance data
   json += "\"balance\":" + DoubleToString(AccountBalance(), 2) + ",";
   json += "\"equity\":" + DoubleToString(AccountEquity(), 2) + ",";
   json += "\"margin\":" + DoubleToString(AccountMargin(), 2) + ",";
   json += "\"free_margin\":" + DoubleToString(AccountFreeMargin(), 2) + ",";
   json += "\"profit\":" + DoubleToString(AccountProfit(), 2) + ",";
   json += "\"leverage\":" + IntegerToString(AccountLeverage()) + ",";
   json += "\"margin_level\":" + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_LEVEL), 2) + ",";
   
   // Open positions count
   int openPositions = 0;
   double floatingPL = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderType() <= OP_SELL)
         {
            openPositions++;
            floatingPL += OrderProfit() + OrderSwap() + OrderCommission();
         }
      }
   }
   json += "\"open_positions\":" + IntegerToString(openPositions) + ",";
   json += "\"floating_pl\":" + DoubleToString(floatingPL, 2) + ",";
   
   // Timestamp
   json += "\"timestamp\":\"" + TimeToString(TimeGMT(), TIME_DATE|TIME_SECONDS) + "\",";
   json += "\"local_time\":\"" + TimeToString(TimeLocal(), TIME_DATE|TIME_SECONDS) + "\"";
   
   json += "}";
   
   return json;
}

//+------------------------------------------------------------------+
//| Write JSON string to file                                          |
//+------------------------------------------------------------------+
bool WriteJSONToFile(string json)
{
   // Delete existing file first
   FileDelete(OutputFileName);
   
   // Open file for writing
   fileHandle = FileOpen(OutputFileName, FILE_WRITE|FILE_TXT|FILE_ANSI);
   
   if(fileHandle == INVALID_HANDLE)
   {
      Print("Error opening file: ", GetLastError());
      return false;
   }
   
   // Write JSON
   FileWriteString(fileHandle, json);
   
   // Close file
   FileClose(fileHandle);
   
   return true;
}

//+------------------------------------------------------------------+
//| Escape special characters for JSON                                 |
//+------------------------------------------------------------------+
string EscapeJSON(string str)
{
   StringReplace(str, "\\", "\\\\");
   StringReplace(str, "\"", "\\\"");
   StringReplace(str, "\n", "\\n");
   StringReplace(str, "\r", "\\r");
   StringReplace(str, "\t", "\\t");
   return str;
}
//+------------------------------------------------------------------+
