//+------------------------------------------------------------------+
//|                               VIKING_MT5_CORE_Account_Writer.mq5 |
//|                                  Copyright 2026, VKNG AI Platform |
//|                                  Version 1.0 - MT5 CORE Account   |
//+------------------------------------------------------------------+
#property copyright "VKNG AI Platform"
#property link      ""
#property version   "1.00"
#property strict

// Input parameters
input int SyncIntervalSeconds = 120;  // Sync interval in seconds
input int MaxClosedDeals = 10000;     // Export ALL deals

// Global variables
string DataFilePath = "viking_mt5_account_885822_data.json";
datetime LastSyncTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("VIKING MT5 CORE Account Writer EA Started (v1.0)");
   Print("Account: ", AccountInfoInteger(ACCOUNT_LOGIN));
   Print("Server: ", AccountInfoString(ACCOUNT_SERVER));
   Print("Broker: ", AccountInfoString(ACCOUNT_COMPANY));
   Print("Data File: ", DataFilePath);
   Print("Sync Interval: ", SyncIntervalSeconds, " seconds");
   Print("Max Closed Deals: ", MaxClosedDeals);
   
   // Write initial data
   WriteAccountData();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("VIKING MT5 CORE Account Writer EA Stopped");
}

//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check if it's time to sync
   datetime currentTime = TimeCurrent();
   
   if(currentTime - LastSyncTime >= SyncIntervalSeconds)
   {
      WriteAccountData();
      LastSyncTime = currentTime;
   }
}

//+------------------------------------------------------------------+
//| Write account data to JSON file                                    |
//+------------------------------------------------------------------+
void WriteAccountData()
{
   int fileHandle = FileOpen(DataFilePath, FILE_WRITE|FILE_TXT|FILE_COMMON);
   
   if(fileHandle == INVALID_HANDLE)
   {
      Print("ERROR: Cannot create data file: ", GetLastError());
      return;
   }
   
   // Start JSON
   FileWriteString(fileHandle, "{\n");
   
   // Account information
   FileWriteString(fileHandle, "  \"account\": " + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + ",\n");
   FileWriteString(fileHandle, "  \"strategy\": \"CORE\",\n");
   FileWriteString(fileHandle, "  \"platform\": \"MT5\",\n");
   FileWriteString(fileHandle, "  \"broker\": \"" + AccountInfoString(ACCOUNT_COMPANY) + "\",\n");
   FileWriteString(fileHandle, "  \"server\": \"" + AccountInfoString(ACCOUNT_SERVER) + "\",\n");
   FileWriteString(fileHandle, "  \"balance\": " + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + ",\n");
   FileWriteString(fileHandle, "  \"equity\": " + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2) + ",\n");
   FileWriteString(fileHandle, "  \"margin\": " + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN), 2) + ",\n");
   FileWriteString(fileHandle, "  \"free_margin\": " + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_FREE), 2) + ",\n");
   
   double marginLevel = 0;
   if(AccountInfoDouble(ACCOUNT_MARGIN) > 0)
      marginLevel = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   
   FileWriteString(fileHandle, "  \"margin_level\": " + DoubleToString(marginLevel, 2) + ",\n");
   FileWriteString(fileHandle, "  \"profit\": " + DoubleToString(AccountInfoDouble(ACCOUNT_PROFIT), 2) + ",\n");
   FileWriteString(fileHandle, "  \"leverage\": " + IntegerToString(AccountInfoInteger(ACCOUNT_LEVERAGE)) + ",\n");
   FileWriteString(fileHandle, "  \"currency\": \"" + AccountInfoString(ACCOUNT_CURRENCY) + "\",\n");
   
   // Timestamp
   FileWriteString(fileHandle, "  \"timestamp\": \"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
   
   // ============================================
   // OPEN POSITIONS
   // ============================================
   FileWriteString(fileHandle, "  \"positions\": [\n");
   
   int totalPositions = PositionsTotal();
   int positionCount = 0;
   
   for(int i = 0; i < totalPositions; i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {
         if(positionCount > 0)
            FileWriteString(fileHandle, ",\n");
         
         FileWriteString(fileHandle, "    {\n");
         FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(ticket) + ",\n");
         FileWriteString(fileHandle, "      \"symbol\": \"" + PositionGetString(POSITION_SYMBOL) + "\",\n");
         FileWriteString(fileHandle, "      \"type\": \"" + (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? "BUY" : "SELL") + "\",\n");
         FileWriteString(fileHandle, "      \"volume\": " + DoubleToString(PositionGetDouble(POSITION_VOLUME), 2) + ",\n");
         FileWriteString(fileHandle, "      \"open_price\": " + DoubleToString(PositionGetDouble(POSITION_PRICE_OPEN), 5) + ",\n");
         FileWriteString(fileHandle, "      \"current_price\": " + DoubleToString(PositionGetDouble(POSITION_PRICE_CURRENT), 5) + ",\n");
         FileWriteString(fileHandle, "      \"profit\": " + DoubleToString(PositionGetDouble(POSITION_PROFIT), 2) + ",\n");
         FileWriteString(fileHandle, "      \"swap\": " + DoubleToString(PositionGetDouble(POSITION_SWAP), 2) + ",\n");
         FileWriteString(fileHandle, "      \"magic\": " + IntegerToString(PositionGetInteger(POSITION_MAGIC)) + ",\n");
         FileWriteString(fileHandle, "      \"open_time\": \"" + TimeToString((datetime)PositionGetInteger(POSITION_TIME), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\"\n");
         FileWriteString(fileHandle, "    }");
         
         positionCount++;
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // ============================================
   // PENDING ORDERS
   // ============================================
   FileWriteString(fileHandle, "  \"orders\": [\n");
   
   int totalOrders = OrdersTotal();
   int orderCount = 0;
   
   for(int i = 0; i < totalOrders; i++)
   {
      ulong ticket = OrderGetTicket(i);
      if(ticket > 0)
      {
         if(orderCount > 0)
            FileWriteString(fileHandle, ",\n");
         
         FileWriteString(fileHandle, "    {\n");
         FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(ticket) + ",\n");
         FileWriteString(fileHandle, "      \"symbol\": \"" + OrderGetString(ORDER_SYMBOL) + "\",\n");
         FileWriteString(fileHandle, "      \"type\": \"" + OrderTypeToString((ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE)) + "\",\n");
         FileWriteString(fileHandle, "      \"volume\": " + DoubleToString(OrderGetDouble(ORDER_VOLUME_CURRENT), 2) + ",\n");
         FileWriteString(fileHandle, "      \"price\": " + DoubleToString(OrderGetDouble(ORDER_PRICE_OPEN), 5) + ",\n");
         FileWriteString(fileHandle, "      \"time\": \"" + TimeToString((datetime)OrderGetInteger(ORDER_TIME_SETUP), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\"\n");
         FileWriteString(fileHandle, "    }");
         
         orderCount++;
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // ============================================
   // CLOSED DEALS HISTORY
   // ============================================
   FileWriteString(fileHandle, "  \"closed_deals\": [\n");
   
   // Select history
   datetime fromDate = D'2024.01.01';
   datetime toDate = TimeCurrent();
   
   if(HistorySelect(fromDate, toDate))
   {
      int historyDeals = HistoryDealsTotal();
      int dealCount = 0;
      
      // Loop from most recent to oldest
      for(int i = historyDeals - 1; i >= 0 && dealCount < MaxClosedDeals; i--)
      {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket > 0)
         {
            ENUM_DEAL_TYPE dealType = (ENUM_DEAL_TYPE)HistoryDealGetInteger(ticket, DEAL_TYPE);
            
            // Only include actual trades (BUY/SELL), not deposits/withdrawals
            if(dealType == DEAL_TYPE_BUY || dealType == DEAL_TYPE_SELL)
            {
               if(dealCount > 0)
                  FileWriteString(fileHandle, ",\n");
               
               FileWriteString(fileHandle, "    {\n");
               FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(ticket) + ",\n");
               FileWriteString(fileHandle, "      \"symbol\": \"" + HistoryDealGetString(ticket, DEAL_SYMBOL) + "\",\n");
               FileWriteString(fileHandle, "      \"type\": \"" + (dealType == DEAL_TYPE_BUY ? "BUY" : "SELL") + "\",\n");
               FileWriteString(fileHandle, "      \"volume\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_VOLUME), 2) + ",\n");
               FileWriteString(fileHandle, "      \"open_price\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_PRICE), 5) + ",\n");
               FileWriteString(fileHandle, "      \"close_price\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_PRICE), 5) + ",\n");
               FileWriteString(fileHandle, "      \"open_time\": \"" + TimeToString((datetime)HistoryDealGetInteger(ticket, DEAL_TIME), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
               FileWriteString(fileHandle, "      \"close_time\": \"" + TimeToString((datetime)HistoryDealGetInteger(ticket, DEAL_TIME), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
               FileWriteString(fileHandle, "      \"profit\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_PROFIT), 2) + ",\n");
               FileWriteString(fileHandle, "      \"swap\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_SWAP), 2) + ",\n");
               FileWriteString(fileHandle, "      \"commission\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_COMMISSION), 2) + ",\n");
               FileWriteString(fileHandle, "      \"magic\": " + IntegerToString(HistoryDealGetInteger(ticket, DEAL_MAGIC)) + ",\n");
               FileWriteString(fileHandle, "      \"comment\": \"" + HistoryDealGetString(ticket, DEAL_COMMENT) + "\"\n");
               FileWriteString(fileHandle, "    }");
               
               dealCount++;
            }
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // ============================================
   // BALANCE OPERATIONS (Deposits/Withdrawals)
   // ============================================
   FileWriteString(fileHandle, "  \"balance_operations\": [\n");
   
   int balanceCount = 0;
   
   if(HistorySelect(fromDate, toDate))
   {
      int historyDeals = HistoryDealsTotal();
      
      for(int i = historyDeals - 1; i >= 0; i--)
      {
         ulong ticket = HistoryDealGetTicket(i);
         if(ticket > 0)
         {
            ENUM_DEAL_TYPE dealType = (ENUM_DEAL_TYPE)HistoryDealGetInteger(ticket, DEAL_TYPE);
            
            // Balance operations
            if(dealType == DEAL_TYPE_BALANCE)
            {
               if(balanceCount > 0)
                  FileWriteString(fileHandle, ",\n");
               
               double amount = HistoryDealGetDouble(ticket, DEAL_PROFIT);
               string opType = amount >= 0 ? "DEPOSIT" : "WITHDRAWAL";
               
               FileWriteString(fileHandle, "    {\n");
               FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(ticket) + ",\n");
               FileWriteString(fileHandle, "      \"type\": \"" + opType + "\",\n");
               FileWriteString(fileHandle, "      \"amount\": " + DoubleToString(amount, 2) + ",\n");
               FileWriteString(fileHandle, "      \"time\": \"" + TimeToString((datetime)HistoryDealGetInteger(ticket, DEAL_TIME), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
               FileWriteString(fileHandle, "      \"comment\": \"" + HistoryDealGetString(ticket, DEAL_COMMENT) + "\"\n");
               FileWriteString(fileHandle, "    }");
               
               balanceCount++;
            }
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // Statistics
   FileWriteString(fileHandle, "  \"positions_count\": " + IntegerToString(positionCount) + ",\n");
   FileWriteString(fileHandle, "  \"orders_count\": " + IntegerToString(orderCount) + ",\n");
   FileWriteString(fileHandle, "  \"closed_deals_count\": " + IntegerToString(HistoryDealsTotal()) + ",\n");
   FileWriteString(fileHandle, "  \"balance_operations_count\": " + IntegerToString(balanceCount) + "\n");
   
   // End JSON
   FileWriteString(fileHandle, "}\n");
   
   FileClose(fileHandle);
   
   Print("MT5 CORE Data written: Balance=", DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2), 
         ", Equity=", DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2),
         ", Positions=", positionCount,
         ", Deals=", HistoryDealsTotal(),
         ", BalanceOps=", balanceCount);
}

//+------------------------------------------------------------------+
//| Convert order type to string                                      |
//+------------------------------------------------------------------+
string OrderTypeToString(ENUM_ORDER_TYPE type)
{
   switch(type)
   {
      case ORDER_TYPE_BUY:             return "BUY";
      case ORDER_TYPE_SELL:            return "SELL";
      case ORDER_TYPE_BUY_LIMIT:       return "BUY_LIMIT";
      case ORDER_TYPE_SELL_LIMIT:      return "SELL_LIMIT";
      case ORDER_TYPE_BUY_STOP:        return "BUY_STOP";
      case ORDER_TYPE_SELL_STOP:       return "SELL_STOP";
      case ORDER_TYPE_BUY_STOP_LIMIT:  return "BUY_STOP_LIMIT";
      case ORDER_TYPE_SELL_STOP_LIMIT: return "SELL_STOP_LIMIT";
      default:                         return "UNKNOWN";
   }
}
