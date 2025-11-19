# MT4 EA Creation Script - Run this on VPS
Write-Host "Creating MT4 Expert Advisor..." -ForegroundColor Yellow

$filePath = "C:\Program Files\MEX Atlantic MT4 Terminal\MQL4\Experts\MT4_Python_Bridge.mq4"

$content = @"
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
    string json = "{";
    json = json + "\"account\":" + IntegerToString(AccountNumber()) + ",";
    json = json + "\"name\":\"" + AccountName() + "\",";
    json = json + "\"server\":\"" + AccountServer() + "\",";
    json = json + "\"balance\":" + DoubleToString(AccountBalance(), 2) + ",";
    json = json + "\"equity\":" + DoubleToString(AccountEquity(), 2) + ",";
    json = json + "\"margin\":" + DoubleToString(AccountMargin(), 2) + ",";
    json = json + "\"free_margin\":" + DoubleToString(AccountFreeMargin(), 2) + ",";
    json = json + "\"profit\":" + DoubleToString(AccountProfit(), 2) + ",";
    json = json + "\"currency\":\"" + AccountCurrency() + "\",";
    json = json + "\"leverage\":" + IntegerToString(AccountLeverage()) + ",";
    json = json + "\"credit\":" + DoubleToString(AccountCredit(), 2) + ",";
    json = json + "\"platform\":\"MT4\",";
    json = json + "\"timestamp\":\"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\"";
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
"@

Set-Content -Path $filePath -Value $content -Encoding UTF8

if (Test-Path $filePath) {
    Write-Host "[SUCCESS] MT4 EA file created" -ForegroundColor Green
    Write-Host "Location: $filePath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Open MT4 Terminal" -ForegroundColor White
    Write-Host "2. Press F4 (MetaEditor)" -ForegroundColor White
    Write-Host "3. File -> Open -> MT4_Python_Bridge.mq4" -ForegroundColor White
    Write-Host "4. Press F7 to compile" -ForegroundColor White
    Write-Host "5. Should show 0 errors" -ForegroundColor White
} else {
    Write-Host "[FAILED] File not created" -ForegroundColor Red
}
