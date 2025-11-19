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
    string address = "tcp://" + ZMQ_HOST + ":" + IntegerToString(ZMQ_PORT);
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
    string q = CharToString(34);
    string json = "{";
    json = json + q + "account" + q + ":" + IntegerToString(AccountNumber()) + ",";
    json = json + q + "name" + q + ":" + q + AccountName() + q + ",";
    json = json + q + "server" + q + ":" + q + AccountServer() + q + ",";
    json = json + q + "balance" + q + ":" + DoubleToString(AccountBalance(), 2) + ",";
    json = json + q + "equity" + q + ":" + DoubleToString(AccountEquity(), 2) + ",";
    json = json + q + "margin" + q + ":" + DoubleToString(AccountMargin(), 2) + ",";
    json = json + q + "free_margin" + q + ":" + DoubleToString(AccountFreeMargin(), 2) + ",";
    json = json + q + "profit" + q + ":" + DoubleToString(AccountProfit(), 2) + ",";
    json = json + q + "currency" + q + ":" + q + AccountCurrency() + q + ",";
    json = json + q + "leverage" + q + ":" + IntegerToString(AccountLeverage()) + ",";
    json = json + q + "credit" + q + ":" + DoubleToString(AccountCredit(), 2) + ",";
    json = json + q + "platform" + q + ":" + q + "MT4" + q + ",";
    json = json + q + "timestamp" + q + ":" + q + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + q;
    json = json + "}";
    
    ZmqMsg message(json);
    socket.send(message);
    Print("Account data sent - Balance: ", AccountBalance(), ", Equity: ", AccountEquity());
}

void OnDeinit(const int reason) {
    string address = "tcp://" + ZMQ_HOST + ":" + IntegerToString(ZMQ_PORT);
    socket.disconnect(address);
    Print("MT4 Bridge stopped");
}
