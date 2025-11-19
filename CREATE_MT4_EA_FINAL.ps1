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
