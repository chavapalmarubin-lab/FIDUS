# 🧪 MT5 Integration Load Testing Plan

## 🎯 **Testing Objectives**

Validate the MT5 Bridge service and FIDUS platform integration can handle:
- Multiple simultaneous MT5 account connections
- High-frequency data requests from multiple users
- Concurrent admin and client dashboard access
- System resilience under load and failure scenarios

---

## 📊 **Load Testing Phases**

### **Phase 1: Basic Connectivity Load Test**
**Objective**: Verify bridge service handles multiple connections

**Test Scenarios:**
1. **Single Account, Multiple Requests**
   - 10 concurrent requests to `/api/mt5/positions`
   - 5 concurrent requests to `/api/mt5/account/info`
   - Measure response times and error rates

2. **Multiple Accounts, Sequential Access**
   - Connect 5 different MT5 accounts
   - Sequential data retrieval from each account
   - Validate data integrity and separation

**Success Criteria:**
- ✅ All requests complete within 10 seconds
- ✅ 0% error rate
- ✅ No data mixing between accounts

### **Phase 2: FIDUS Platform Load Test**
**Objective**: Test platform handling of MT5 data under load

**Test Scenarios:**
1. **Multiple Admin Users**
   - 3 admin users accessing MT5 management simultaneously
   - Concurrent MT5 account creation and modification
   - Simultaneous system status monitoring

2. **Multiple Client Dashboards**
   - 10 clients viewing MT5 data simultaneously
   - Real-time position updates for all users
   - Concurrent balance and equity monitoring

**Success Criteria:**
- ✅ Dashboard loads within 5 seconds for all users
- ✅ Data updates appear within 30 seconds
- ✅ No authentication or authorization conflicts

### **Phase 3: High-Volume Data Test**
**Objective**: Validate system performance with realistic data volumes

**Test Scenarios:**
1. **Large Position Sets**
   - Test accounts with 50+ open positions
   - Retrieve complete position history (1 year)
   - Handle accounts with extensive trading history

2. **Rapid Data Updates**
   - Simulate high-frequency trading scenarios
   - Test position updates every 1-2 seconds
   - Validate real-time balance changes

**Success Criteria:**
- ✅ Position retrieval completes within 15 seconds
- ✅ System handles up to 100 positions per account
- ✅ Real-time updates don't degrade performance

---

## 🔧 **Load Testing Tools & Scripts**

### **Tool 1: Bridge Service Load Tester**

```python
# Load test script for MT5 Bridge service
import asyncio
import aiohttp
import time
from datetime import datetime

async def load_test_bridge_service():
    """Concurrent load test for MT5 Bridge"""
    
    bridge_url = "http://217.197.163.11:8000"
    api_key = "fidus-mt5-bridge-key-2025-secure"
    headers = {"X-API-Key": api_key}
    
    # Test scenarios
    test_endpoints = [
        "/",
        "/health", 
        "/api/mt5/status",
        "/api/mt5/positions",
        "/api/mt5/symbols"
    ]
    
    concurrent_requests = 20
    total_requests = 100
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for endpoint in test_endpoints:
            print(f"Load testing {endpoint}...")
            
            start_time = time.time()
            
            # Create concurrent requests
            tasks = []
            for i in range(total_requests):
                task = session.get(f"{bridge_url}{endpoint}")
                tasks.append(task)
                
                # Batch requests for concurrency control
                if len(tasks) >= concurrent_requests:
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []
            
            # Process remaining requests
            if tasks:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"  Completed {total_requests} requests in {duration:.2f}s")
            print(f"  Average: {duration/total_requests:.3f}s per request")
```

### **Tool 2: FIDUS Platform Load Tester**

```python
# Load test script for FIDUS MT5 endpoints
import requests
import threading
import time
from datetime import datetime

def test_fidus_mt5_endpoints():
    """Multi-user load test for FIDUS platform"""
    
    base_url = "https://fidus-invest.emergent.host/api"
    
    # Login as admin
    login_response = requests.post(f"{base_url}/auth/login", 
        json={"username": "admin", "password": "password123", "user_type": "admin"})
    
    if login_response.status_code != 200:
        print("❌ Admin login failed")
        return
    
    token = login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # MT5 endpoints to test
    endpoints = [
        "/mt5/brokers",
        "/mt5/admin/accounts", 
        "/mt5/admin/performance/overview",
        "/mt5/admin/system-status"
    ]
    
    def worker_thread(thread_id, endpoint):
        """Worker thread for concurrent testing"""
        for i in range(10):  # 10 requests per thread
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=30)
                print(f"Thread {thread_id}: {endpoint} -> {response.status_code}")
                time.sleep(1)  # 1 second between requests
            except Exception as e:
                print(f"Thread {thread_id}: Error -> {e}")
    
    # Create concurrent threads
    threads = []
    for endpoint in endpoints:
        for thread_id in range(3):  # 3 threads per endpoint
            thread = threading.Thread(target=worker_thread, args=(thread_id, endpoint))
            threads.append(thread)
            thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("✅ Load test completed")
```

---

## 📈 **Performance Benchmarks**

### **Baseline Performance Targets:**

| Metric | Target | Acceptable | Critical |
|--------|---------|------------|----------|
| Bridge Response Time | < 2s | < 5s | > 10s |
| Dashboard Load Time | < 3s | < 7s | > 15s |
| MT5 Data Sync | < 30s | < 60s | > 120s |
| Concurrent Users | 50+ | 20+ | < 10 |
| Error Rate | 0% | < 1% | > 5% |

### **Resource Utilization Limits:**

| Resource | Normal | Warning | Critical |
|----------|---------|---------|----------|
| CPU Usage | < 50% | < 80% | > 90% |
| Memory Usage | < 70% | < 85% | > 95% |
| Network I/O | < 100 MB/min | < 500 MB/min | > 1 GB/min |
| Database Connections | < 50 | < 100 | > 150 |

---

## 🚨 **Failure Scenarios Testing**

### **Test 1: MT5 Bridge Service Failure**
**Scenario**: Bridge service becomes unavailable during peak usage
- **Expected Behavior**: FIDUS shows cached data with "Last Updated" timestamps
- **Recovery Test**: Verify automatic reconnection when service restores
- **User Experience**: Error messages are clear and non-technical

### **Test 2: MT5 Terminal Disconnection**  
**Scenario**: MT5 terminal loses connection to broker
- **Expected Behavior**: Bridge service reports "MT5 not connected" status
- **Recovery Test**: Automatic retry when MT5 reconnects
- **User Experience**: Dashboard shows "Connecting..." status

### **Test 3: Database Connection Issues**
**Scenario**: MongoDB connection becomes unstable
- **Expected Behavior**: Graceful degradation with cached MT5 data
- **Recovery Test**: Database reconnection without data loss
- **User Experience**: Platform remains functional with read-only mode

### **Test 4: High Network Latency**
**Scenario**: Slow connection between FIDUS and VPS bridge
- **Expected Behavior**: Timeout handling with retry mechanisms
- **Recovery Test**: Performance recovery when latency improves
- **User Experience**: Loading indicators and timeout messages

---

## 📋 **Load Testing Execution Plan**

### **Pre-Testing Setup:**
1. ✅ Ensure MT5 Bridge service is operational on VPS
2. ✅ Configure test MT5 accounts with known data
3. ✅ Set up monitoring for system resources
4. ✅ Create baseline performance measurements

### **Testing Schedule:**
- **Week 1**: Phase 1 - Basic connectivity load tests
- **Week 2**: Phase 2 - Platform integration load tests  
- **Week 3**: Phase 3 - High-volume data tests
- **Week 4**: Failure scenario and recovery tests

### **Success Validation:**
- **Performance Metrics**: All targets met or exceeded
- **Error Handling**: Graceful degradation under load
- **User Experience**: No impact on normal platform operations
- **Data Integrity**: No data corruption or mixing under load

### **Post-Testing Actions:**
- **Performance Optimization**: Address any bottlenecks identified
- **Monitoring Setup**: Implement ongoing performance monitoring
- **Capacity Planning**: Document recommended user/account limits
- **Production Deployment**: Deploy with confidence in system scalability

---

**🎯 This load testing plan ensures the MT5 integration can handle production workloads while maintaining excellent user experience and data integrity.**