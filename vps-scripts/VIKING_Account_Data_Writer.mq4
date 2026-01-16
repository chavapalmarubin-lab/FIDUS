//+------------------------------------------------------------------+
//|                                    VIKING_Account_Data_Writer.mq4 |
//|                                  Copyright 2025, VKNG AI Platform |
//|                                  Version 3.0 - With Balance Ops   |
//+------------------------------------------------------------------+
#property copyright "VKNG AI Platform"
#property link      ""
#property version   "3.00"
#property strict

// Input parameters
input int SyncIntervalSeconds = 120;  // Sync interval in seconds
input int MaxClosedTrades = 10000;    // Export ALL trades (increased from 100)

// Global variables
string DataFilePath = "viking_account_33627673_data.json";
datetime LastSyncTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("VIKING Account Data Writer EA Started (v3.0 with Balance Operations)");
   Print("Account: ", AccountNumber());
   Print("Server: ", AccountServer());
   Print("Data File: ", DataFilePath);
   Print("Sync Interval: ", SyncIntervalSeconds, " seconds");
   Print("Max Closed Trades: ", MaxClosedTrades);
   
   // Write initial data
   WriteAccountData();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("VIKING Account Data Writer EA Stopped");
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
   FileWriteString(fileHandle, "  \"strategy\": \"CORE\",\n");
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
   
   // ============================================
   // OPEN POSITIONS (MODE_TRADES)
   // ============================================
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
            FileWriteString(fileHandle, "      \"open_time\": \"" + TimeToString(OrderOpenTime(), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\"\n");
            FileWriteString(fileHandle, "    }");
            
            positionCount++;
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // ============================================
   // PENDING ORDERS
   // ============================================
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
            FileWriteString(fileHandle, "      \"open_time\": \"" + TimeToString(OrderOpenTime(), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\"\n");
            FileWriteString(fileHandle, "    }");
            
            orderCount++;
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // ============================================
   // CLOSED TRADES HISTORY (MODE_HISTORY)
   // ============================================
   FileWriteString(fileHandle, "  \"closed_trades\": [\n");
   
   int historyTotal = OrdersHistoryTotal();
   int historyCount = 0;
   
   // Loop from most recent to oldest
   for(i = historyTotal - 1; i >= 0 && historyCount < MaxClosedTrades; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY))
      {
         // Only include actual trades (BUY=0, SELL=1), not deposits/withdrawals
         if(OrderType() <= 1)
         {
            if(historyCount > 0)
               FileWriteString(fileHandle, ",\n");
            
            FileWriteString(fileHandle, "    {\n");
            FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(OrderTicket()) + ",\n");
            FileWriteString(fileHandle, "      \"symbol\": \"" + OrderSymbol() + "\",\n");
            FileWriteString(fileHandle, "      \"type\": \"" + OrderTypeToString(OrderType()) + "\",\n");
            FileWriteString(fileHandle, "      \"volume\": " + DoubleToString(OrderLots(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"open_price\": " + DoubleToString(OrderOpenPrice(), 5) + ",\n");
            FileWriteString(fileHandle, "      \"close_price\": " + DoubleToString(OrderClosePrice(), 5) + ",\n");
            FileWriteString(fileHandle, "      \"open_time\": \"" + TimeToString(OrderOpenTime(), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
            FileWriteString(fileHandle, "      \"close_time\": \"" + TimeToString(OrderCloseTime(), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
            FileWriteString(fileHandle, "      \"profit\": " + DoubleToString(OrderProfit(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"swap\": " + DoubleToString(OrderSwap(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"commission\": " + DoubleToString(OrderCommission(), 2) + "\n");
            FileWriteString(fileHandle, "    }");
            
            historyCount++;
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // ============================================
   // BALANCE OPERATIONS (Deposits/Withdrawals)
   // OrderType() == 6 is OP_BALANCE
   // ============================================
   FileWriteString(fileHandle, "  \"balance_operations\": [\n");
   
   int balanceCount = 0;
   
   for(i = historyTotal - 1; i >= 0; i--)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_HISTORY))
      {
         // Balance operations have OrderType() == 6 (OP_BALANCE)
         // No symbol, profit field contains the deposit/withdrawal amount
         if(OrderType() == 6)
         {
            if(balanceCount > 0)
               FileWriteString(fileHandle, ",\n");
            
            // Determine type based on profit sign
            string opType = "DEPOSIT";
            if(OrderProfit() < 0)
               opType = "WITHDRAWAL";
            
            FileWriteString(fileHandle, "    {\n");
            FileWriteString(fileHandle, "      \"ticket\": " + IntegerToString(OrderTicket()) + ",\n");
            FileWriteString(fileHandle, "      \"type\": \"" + opType + "\",\n");
            FileWriteString(fileHandle, "      \"amount\": " + DoubleToString(OrderProfit(), 2) + ",\n");
            FileWriteString(fileHandle, "      \"time\": \"" + TimeToString(OrderCloseTime(), TIME_DATE|TIME_MINUTES|TIME_SECONDS) + "\",\n");
            FileWriteString(fileHandle, "      \"comment\": \"" + OrderComment() + "\"\n");
            FileWriteString(fileHandle, "    }");
            
            balanceCount++;
         }
      }
   }
   
   FileWriteString(fileHandle, "\n  ],\n");
   
   // Statistics
   FileWriteString(fileHandle, "  \"positions_count\": " + IntegerToString(positionCount) + ",\n");
   FileWriteString(fileHandle, "  \"orders_count\": " + IntegerToString(orderCount) + ",\n");
   FileWriteString(fileHandle, "  \"closed_trades_count\": " + IntegerToString(historyCount) + ",\n");
   FileWriteString(fileHandle, "  \"balance_operations_count\": " + IntegerToString(balanceCount) + ",\n");
   FileWriteString(fileHandle, "  \"history_total\": " + IntegerToString(historyTotal) + "\n");
   
   // End JSON
   FileWriteString(fileHandle, "}\n");
   
   FileClose(fileHandle);
   
   Print("Data written: Balance=", DoubleToString(AccountBalance(), 2), 
         ", Equity=", DoubleToString(AccountEquity(), 2),
         ", Positions=", positionCount,
         ", Orders=", orderCount,
         ", ClosedTrades=", historyCount,
         ", BalanceOps=", balanceCount);
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
