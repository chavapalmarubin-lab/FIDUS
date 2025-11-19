//+------------------------------------------------------------------+
//|                                          MT4_Python_Bridge.mq4   |
//|                                       FIDUS Investment Platform  |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "FIDUS Investment Management"
#property link      "https://fidus-investment.com"
#property version   "1.00"
#property strict

#include <Zmq/Zmq.mqh>

// ZeroMQ Configuration
extern string ZEROMQ_PROTOCOL = "tcp";
extern string ZEROMQ_HOST = "localhost";
extern int ZEROMQ_PUSH_PORT = 32768;
extern int ZEROMQ_PULL_PORT = 32769;
extern int ZEROMQ_PUB_PORT = 32770;

// Data Update Configuration
extern int UPDATE_INTERVAL_SECONDS = 300; // 5 minutes (same as MT5)
extern bool ENABLE_DEBUG = true;

// ZeroMQ Context and Sockets
Context context("MT4_BRIDGE");
Socket pushSocket(context, ZMQ_PUSH);
Socket pullSocket(context, ZMQ_PULL);
Socket pubSocket(context, ZMQ_PUB);

// Timing
datetime lastUpdate = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
    // Print account info
    Print("=================================");
    Print("MT4 Python Bridge Initialized");
    Print("Account: ", AccountNumber());
    Print("Server: ", AccountServer());
    Print("Name: ", AccountName());
    Print("=================================");
    
    // Bind ZeroMQ sockets
    string pushAddress = StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, ZEROMQ_HOST, ZEROMQ_PUSH_PORT);
    string pullAddress = StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, ZEROMQ_HOST, ZEROMQ_PULL_PORT);
    string pubAddress = StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, ZEROMQ_HOST, ZEROMQ_PUB_PORT);
    
    if(!pushSocket.bind(pushAddress))
    {
        Print("ERROR: Failed to bind PUSH socket on ", pushAddress);
        return(INIT_FAILED);
    }
    
    if(!pullSocket.bind(pullAddress))
    {
        Print("ERROR: Failed to bind PULL socket on ", pullAddress);
        return(INIT_FAILED);
    }
    
    if(!pubSocket.bind(pubAddress))
    {
        Print("ERROR: Failed to bind PUB socket on ", pubAddress);
        return(INIT_FAILED);
    }
    
    Print("ZeroMQ sockets bound successfully");
    Print("PUSH: ", pushAddress);
    Print("PULL: ", pullAddress);
    Print("PUB: ", pubAddress);
    
    // Send initial data
    SendAccountData();
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("MT4 Python Bridge Shutdown. Reason: ", reason);
    
    // Close sockets
    pushSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, ZEROMQ_HOST, ZEROMQ_PUSH_PORT));
    pullSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, ZEROMQ_HOST, ZEROMQ_PULL_PORT));
    pubSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, ZEROMQ_HOST, ZEROMQ_PUB_PORT));
}

//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check if it's time to update
    if(TimeCurrent() - lastUpdate >= UPDATE_INTERVAL_SECONDS)
    {
        SendAccountData();
        lastUpdate = TimeCurrent();
    }
    
    // Process incoming commands
    ProcessCommands();
}

//+------------------------------------------------------------------+
//| Send account data to Python via ZeroMQ                            |
//+------------------------------------------------------------------+
void SendAccountData()
{
    // Build JSON with account data (matching MT5 format)
    string json = "{";
    json += StringFormat("\"account\": %d,", AccountNumber());
    json += StringFormat("\"server\": \"%s\",", AccountServer());
    json += StringFormat("\"name\": \"%s\",", AccountName());
    json += StringFormat("\"balance\": %.2f,", AccountBalance());
    json += StringFormat("\"equity\": %.2f,", AccountEquity());
    json += StringFormat("\"margin\": %.2f,", AccountMargin());
    json += StringFormat("\"free_margin\": %.2f,", AccountFreeMargin());
    json += StringFormat("\"profit\": %.2f,", AccountProfit());
    json += StringFormat("\"currency\": \"%s\",", AccountCurrency());
    json += StringFormat("\"leverage\": %d,", AccountLeverage());
    json += StringFormat("\"credit\": %.2f,", AccountCredit());
    json += StringFormat("\"timestamp\": \"%s\",", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS));
    json += StringFormat("\"platform\": \"MT4\",");
    json += StringFormat("\"fund_type\": \"MONEY_MANAGER\",");
    json += StringFormat("\"client_name\": \"Money Manager MT4 Account\",");
    json += StringFormat("\"success\": true");
    json += "}";
    
    // Send via PUSH socket
    ZmqMsg message(json);
    pushSocket.send(message);
    
    if(ENABLE_DEBUG)
    {
        Print("Account data sent: ", json);
    }
    
    // Publish to PUB socket (for monitoring)
    pubSocket.send(message);
}

//+------------------------------------------------------------------+
//| Process commands from Python                                      |
//+------------------------------------------------------------------+
void ProcessCommands()
{
    ZmqMsg request;
    
    // Non-blocking receive
    if(pullSocket.recv(request, true))
    {
        string command = request.getData();
        
        if(ENABLE_DEBUG)
        {
            Print("Received command: ", command);
        }
        
        // Parse and execute command
        if(StringFind(command, "GET_ACCOUNT_INFO") >= 0)
        {
            SendAccountData();
        }
        else if(StringFind(command, "GET_POSITIONS") >= 0)
        {
            SendOpenPositions();
        }
        else if(StringFind(command, "GET_HISTORY") >= 0)
        {
            SendTradeHistory();
        }
        else if(StringFind(command, "PING") >= 0)
        {
            // Health check response
            ZmqMsg pong("PONG");
            pushSocket.send(pong);
        }
    }
}

//+------------------------------------------------------------------+
//| Send open positions                                               |
//+------------------------------------------------------------------+
void SendOpenPositions()
{
    string json = "[";
    
    for(int i = 0; i < OrdersTotal(); i++)
    {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
        
        if(i > 0) json += ",";
        
        json += "{";
        json += StringFormat("\"ticket\": %d,", OrderTicket());
        json += StringFormat("\"symbol\": \"%s\",", OrderSymbol());
        json += StringFormat("\"type\": %d,", OrderType());
        json += StringFormat("\"lots\": %.2f,", OrderLots());
        json += StringFormat("\"open_price\": %.5f,", OrderOpenPrice());
        json += StringFormat("\"current_price\": %.5f,", OrderType() == OP_BUY ? MarketInfo(OrderSymbol(), MODE_BID) : MarketInfo(OrderSymbol(), MODE_ASK));
        json += StringFormat("\"profit\": %.2f,", OrderProfit());
        json += StringFormat("\"commission\": %.2f,", OrderCommission());
        json += StringFormat("\"swap\": %.2f,", OrderSwap());
        json += StringFormat("\"open_time\": \"%s\"", TimeToString(OrderOpenTime(), TIME_DATE|TIME_SECONDS));
        json += "}";
    }
    
    json += "]";
    
    ZmqMsg message(json);
    pushSocket.send(message);
    
    if(ENABLE_DEBUG)
    {
        Print("Positions sent: ", json);
    }
}

//+------------------------------------------------------------------+
//| Send trade history                                                |
//+------------------------------------------------------------------+
void SendTradeHistory()
{
    string json = "[";
    int count = 0;
    
    // Get last 100 closed trades
    for(int i = OrdersHistoryTotal() - 1; i >= 0 && count < 100; i--)
    {
        if(!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;
        
        if(count > 0) json += ",";
        
        json += "{";
        json += StringFormat("\"ticket\": %d,", OrderTicket());
        json += StringFormat("\"symbol\": \"%s\",", OrderSymbol());
        json += StringFormat("\"type\": %d,", OrderType());
        json += StringFormat("\"lots\": %.2f,", OrderLots());
        json += StringFormat("\"open_price\": %.5f,", OrderOpenPrice());
        json += StringFormat("\"close_price\": %.5f,", OrderClosePrice());
        json += StringFormat("\"profit\": %.2f,", OrderProfit());
        json += StringFormat("\"commission\": %.2f,", OrderCommission());
        json += StringFormat("\"swap\": %.2f,", OrderSwap());
        json += StringFormat("\"open_time\": \"%s\",", TimeToString(OrderOpenTime(), TIME_DATE|TIME_SECONDS));
        json += StringFormat("\"close_time\": \"%s\"", TimeToString(OrderCloseTime(), TIME_DATE|TIME_SECONDS));
        json += "}";
        
        count++;
    }
    
    json += "]";
    
    ZmqMsg message(json);
    pushSocket.send(message);
    
    if(ENABLE_DEBUG)
    {
        Print("Trade history sent: ", json);
    }
}
//+------------------------------------------------------------------+