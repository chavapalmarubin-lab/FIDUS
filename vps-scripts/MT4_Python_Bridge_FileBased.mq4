//+------------------------------------------------------------------+
//|                                   MT4_Python_Bridge_FileBased.mq4|
//|                                  FIDUS Investment Management     |
//+------------------------------------------------------------------+
#property copyright "FIDUS Investment Management"
#property strict

input int UPDATE_INTERVAL = 300; // Update every 5 minutes
input string OUTPUT_FILE = "C:\\mt4_bridge\\account_data.json";

datetime lastUpdate = 0;

int OnInit() {
    Print("MT4 File-Based Bridge initialized");
    Print("Output file: ", OUTPUT_FILE);
    WriteAccountData();
    return INIT_SUCCEEDED;
}

void OnTick() {
    if (TimeCurrent() - lastUpdate >= UPDATE_INTERVAL) {
        WriteAccountData();
        lastUpdate = TimeCurrent();
    }
}

void WriteAccountData() {
    // Build JSON string
    string json = "";
    json = json + "{\n";
    json = json + "  \"account\": " + IntegerToString(AccountNumber()) + ",\n";
    json = json + "  \"name\": \"" + AccountName() + "\",\n";
    json = json + "  \"server\": \"" + AccountServer() + "\",\n";
    json = json + "  \"balance\": " + DoubleToString(AccountBalance(), 2) + ",\n";
    json = json + "  \"equity\": " + DoubleToString(AccountEquity(), 2) + ",\n";
    json = json + "  \"margin\": " + DoubleToString(AccountMargin(), 2) + ",\n";
    json = json + "  \"free_margin\": " + DoubleToString(AccountFreeMargin(), 2) + ",\n";
    json = json + "  \"profit\": " + DoubleToString(AccountProfit(), 2) + ",\n";
    json = json + "  \"currency\": \"" + AccountCurrency() + "\",\n";
    json = json + "  \"leverage\": " + IntegerToString(AccountLeverage()) + ",\n";
    json = json + "  \"credit\": " + DoubleToString(AccountCredit(), 2) + ",\n";
    json = json + "  \"platform\": \"MT4\",\n";
    json = json + "  \"timestamp\": \"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\"\n";
    json = json + "}\n";
    
    // Write to file
    int handle = FileOpen(OUTPUT_FILE, FILE_WRITE|FILE_TXT);
    if (handle != INVALID_HANDLE) {
        FileWriteString(handle, json);
        FileClose(handle);
        Print("Account data written - Balance: ", AccountBalance(), ", Equity: ", AccountEquity());
    } else {
        Print("ERROR: Could not write to file: ", OUTPUT_FILE);
    }
}

void OnDeinit(const int reason) {
    Print("MT4 File-Based Bridge stopped");
}
