//+------------------------------------------------------------------+
//|                                    MT4_Account_Data_Writer.mq4   |
//|                                  Copyright 2025, FIDUS Platform  |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "FIDUS Platform"
#property link      ""
#property version   "1.00"
#property strict

// Input parameters
input int SyncIntervalSeconds = 120;  // Sync interval in seconds

// Global variables
string DataFilePath = "account_33200931_data.json";
datetime LastSyncTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("MT4 Account Data Writer EA Started");
   Print("Account: ", AccountNumber());
   Print("Server: ", AccountServer());
   Print("Data File: ", DataFilePath);
   Print("Sync Interval: ", SyncIntervalSeconds, " seconds");
   
   // Write initial data
   WriteAccountData();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("MT4 Account Data Writer EA Stopped");
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
   FileWriteString(fileHandle, "  \"account\": " + IntegerToString(AccountNumber()) + ",\n");
   FileWriteString(fileHandle, "  \"server\": \"" + AccountServer() + "\",\n");
   FileWriteString(fileHandle, "  \"balance\": " + DoubleToString(AccountBalance(), 2) + ",\n");
   FileWriteString(fileHandle, "  \"equity\": " + DoubleToString(AccountEquity(), 2) + ",\n");
   FileWriteString(fileHandle, "  \"margin\": " + DoubleToString(AccountMargin(), 2) + ",\n");
   FileWriteString(fileHandle, "  \"free_margin\": " + DoubleToString(AccountFreeMargin(), 2) + ",\n");
   
   double marginLevel = 0;
   if(AccountMargin() > 0)
      marginLevel = AccountEquity() / AccountMargin() * 100;
   
   FileWriteString(fileHandle, "  \"margin_level\": " + DoubleToString(marginLevel, 2) + ",\n");
   FileWriteString(fileHandle, "  \"profit\": " + DoubleToString(AccountProfit(), 2) + ",\n");
   FileWriteString(fileHandle, "  \"leverage\": " + IntegerToString(AccountLeverage()) + ",\n");
   FileWriteString(fileHandle, "  \"currency\": \"" + AccountCurrency() + "\",\n");
   
   // Timestamp
   FileWriteString(fileHandle, "  \"timestamp\": \"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
   
   // Open positions
   FileWriteString(fileHandle, "  \"positions\": [\n");
   
   int totalOrders = OrdersTotal();
   int positionCount = 0;
   int i;
   
   for(i = 0; i < totalOrders; i++)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderType() <= 1)  // Buy or Sell
         {
            if(positionCount > 0)
               FileWriteString(fileHandle, ",\n");
            
            FileWriteString(fileHandle, "    {\n");
            FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(OrderTicket()) + ",\n");
            FileWriteString(fileHandle, "      \"symbol\": \"" + OrderSymbol() + "\",\n");
            FileWriteString(fileHandle, "      \"type\": \"" + OrderTypeToString(OrderType()) + "\",\n");
            FileWriteString(fileHandle, "      \"volume\": " + DoubleToString(OrderLots(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"open_price\": " + DoubleToString(OrderOpenPrice(), 5) + ",\n");
            FileWriteString(fileHandle, "      \"current_price\": " + DoubleToString(OrderClosePrice(), 5) + ",\n");
            FileWriteString(fileHandle, "      \"profit\": " + DoubleToString(OrderProfit(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"swap\": " + DoubleToString(OrderSwap(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"commission\": " + DoubleToString(OrderCommission(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"open_time\": \"" + TimeToString(OrderOpenTime(), TIME_DATE|TIME_MINUTES) + "\"\n");
            FileWriteString(fileHandle, "    }");
            
            positionCount++;
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // Pending orders
   FileWriteString(fileHandle, "  \"orders\": [\n");
   
   int orderCount = 0;
   
   for(i = 0; i < totalOrders; i++)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderType() > 1)  // Pending orders
         {
            if(orderCount > 0)
               FileWriteString(fileHandle, ",\n");
            
            FileWriteString(fileHandle, "    {\n");
            FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(OrderTicket()) + ",\n");
            FileWriteString(fileHandle, "      \"symbol\": \"" + OrderSymbol() + "\",\n");
            FileWriteString(fileHandle, "      \"type\": \"" + OrderTypeToString(OrderType()) + "\",\n");
            FileWriteString(fileHandle, "      \"volume\": " + DoubleToString(OrderLots(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"open_price\": " + DoubleToString(OrderOpenPrice(), 5) + ",\n");
            FileWriteString(fileHandle, "      \"open_time\": \"" + TimeToString(OrderOpenTime(), TIME_DATE|TIME_MINUTES) + "\"\n");
            FileWriteString(fileHandle, "    }");
            
            orderCount++;
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // Statistics
   FileWriteString(fileHandle, "  \"positions_count\": " + IntegerToString(positionCount) + ",\n");
   FileWriteString(fileHandle, "  \"orders_count\": " + IntegerToString(orderCount) + "\n");
   
   // End JSON
   FileWriteString(fileHandle, "}\n");
   
   FileClose(fileHandle);
   
   Print("Data written: Balance=", DoubleToString(AccountBalance(), 2), 
         ", Equity=", DoubleToString(AccountEquity(), 2),
         ", Positions=", positionCount,
         ", Orders=", orderCount);
}

//+------------------------------------------------------------------+
//| Convert order type to string                                      |
//+------------------------------------------------------------------+
string OrderTypeToString(int type)
{
   switch(type)
   {
      case OP_BUY:       return "BUY";
      case OP_SELL:      return "SELL";
      case OP_BUYLIMIT:  return "BUY_LIMIT";
      case OP_SELLLIMIT: return "SELL_LIMIT";
      case OP_BUYSTOP:   return "BUY_STOP";
      case OP_SELLSTOP:  return "SELL_STOP";
      default:           return "UNKNOWN";
   }
}
