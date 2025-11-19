//+------------------------------------------------------------------+
//|                                          MT4_Python_Bridge.mq4   |
//+------------------------------------------------------------------+
#property copyright "FIDUS Investment Management"
#property strict

#include <Zmq/Zmq.mqh>

input int UPDATE_INTERVAL = 300;
input string ZMQ_HOST = "localhost";
input int ZMQ_PORT = 32768;

datetime lastUpdate = 0;
Context context("MT4_BRIDGE");
Socket socket(context, ZMQ_PUSH);

int OnInit() {
    string address = StringFormat("tcp://%s:%d", ZMQ_HOST, ZMQ_PORT);
    socket.connect(address);
    Print("MT4 Bridge initialized, connecting to ", address);
    SendAccountData();
    return INIT_SUCCEEDED;
}

void OnTick() {
    if (TimeCurrent() - lastUpdate >= UPDATE_INTERVAL) {
        SendAccountData();
        lastUpdate = TimeCurrent();
    }
}

void SendAccountData() {
    string json = "{";
    json += StringFormat("\"account\": %d,", AccountNumber());
    json += StringFormat("\"name\": \"%s\",", AccountName());
    json += StringFormat("\"server\": \"%s\",", AccountServer());
    json += StringFormat("\"balance\": %.2f,", AccountBalance());
    json += StringFormat("\"equity\": %.2f,", AccountEquity());
    json += StringFormat("\"margin\": %.2f,", AccountMargin());
    json += StringFormat("\"free_margin\": %.2f,", AccountFreeMargin());
    json += StringFormat("\"profit\": %.2f,", AccountProfit());
    json += StringFormat("\"currency\": \"%s\",", AccountCurrency());
    json += StringFormat("\"leverage\": %d,", AccountLeverage());
    json += StringFormat("\"credit\": %.2f,", AccountCredit());
    json += StringFormat("\"platform\": \"MT4\",");
    json += StringFormat("\"timestamp\": \"%s\"", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS));
    json += "}";
    
    ZmqMsg message(json);
    socket.send(message);
    Print("Account data sent - Balance: ", AccountBalance(), ", Equity: ", AccountEquity());
}

void OnDeinit(const int reason) {
    socket.disconnect(StringFormat("tcp://%s:%d", ZMQ_HOST, ZMQ_PORT));
    Print("MT4 Bridge stopped");
}
