# File-Based MT4 Bridge Solution

## Why This Approach?

After 11+ hours trying to get mql-zmq to compile, we switched to a **file-based approach** that:

✅ **Works immediately** - No external libraries  
✅ **No compilation errors** - Uses native MT4 file I/O  
✅ **Easy to debug** - You can see the JSON file  
✅ **More reliable** - No DLL dependencies  

## How It Works

```
MT4 EA (every 5 min) → writes JSON file → Python service → MongoDB
```

1. **MT4 EA** writes account data to `C:\mt4_bridge\account_data.json`
2. **Python service** monitors the file and uploads to MongoDB when updated

## Deployment Steps

### 1. Deploy via GitHub Actions

Go to: **Actions** → **"Deploy File-Based MT4 Bridge (NO ZMQ)"** → **Run workflow**

### 2. Compile the EA

1. Open **MetaEditor** on your VPS
2. Open `MT4_Python_Bridge_FileBased.mq4`
3. Press **F7** to compile
4. Should show **0 errors** (no DLL imports needed!)

### 3. Attach EA to Chart

1. In MT4, drag the EA from Navigator to any chart
2. Check MT4 Journal - should see "MT4 File-Based Bridge initialized"
3. Check file is being created: `C:\mt4_bridge\account_data.json`

### 4. Start Python Service

```powershell
cd C:\mt4_bridge_service
python mt4_file_bridge_service.py
```

Or use Task Scheduler to run on startup.

## Files Created

- `MT4_Python_Bridge_FileBased.mq4` - File-based EA (NO ZMQ)
- `mt4_file_bridge_service.py` - Python service that reads the file
- `C:\mt4_bridge\account_data.json` - Data file (created by EA)

## Advantages Over ZeroMQ

| Feature | File-Based | ZeroMQ |
|---------|------------|--------|
| Compilation | ✅ Always works | ❌ Library compatibility issues |
| Dependencies | ✅ None | ❌ DLLs, external libs |
| Debugging | ✅ Easy - view JSON file | ❌ Network debugging |
| Reliability | ✅ File I/O is native | ❌ Socket connections can fail |
| Setup time | ✅ 5 minutes | ❌ 11+ hours (still broken) |

## Testing

1. Check EA is writing file:
   ```powershell
   Get-Content C:\mt4_bridge\account_data.json
   ```

2. Check Python service is reading:
   ```powershell
   # Should see "File updated" messages in console
   ```

3. Check MongoDB:
   ```javascript
   db.mt5_accounts.findOne({_id: "MT4_33200931"})
   ```

## Configuration

Edit the EA input parameters if needed:
- `UPDATE_INTERVAL` - Update frequency in seconds (default: 300 = 5 minutes)
- `OUTPUT_FILE` - Path to JSON file (default: `C:\mt4_bridge\account_data.json`)

## Troubleshooting

**EA not writing file?**
- Check MT4 Journal for error messages
- Ensure `C:\mt4_bridge` directory exists
- Check MT4 has file write permissions

**Python service not reading file?**
- Check file path matches EA setting
- Ensure MongoDB connection string is correct in `.env`
- Check file modification time is updating

## Why ZeroMQ Failed

The `mql-zmq` library has known compatibility issues with certain MT4 builds. After multiple attempts:
- 17 compilation errors even with library installed
- Variable naming issues (`message` vs `msg`)
- DLL import complications
- Socket connection unreliability

**The file-based approach eliminates all of these problems.**
