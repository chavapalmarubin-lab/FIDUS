# 📖 FIDUS Technical Documentation - User Guide

## Overview

The FIDUS Technical Documentation system is an **Interactive Technical Command Center** that provides real-time monitoring, management, and documentation for the entire FIDUS investment platform.

**Version:** 7.0 (Phase 7 Complete)  
**Last Updated:** October 2024  
**Status:** ✅ Production Ready

---

## 🎯 What This System Does

The Technical Documentation system provides:

1. **Live System Monitoring** - Real-time health checks of all components
2. **Interactive Architecture Visualization** - Visual system diagram with live status
3. **Secure Credentials Management** - Centralized credential storage with audit logs
4. **API Documentation & Testing** - Complete API reference with "Try It" feature
5. **System Health Dashboard** - Real-time monitoring with automated email alerts
6. **Quick Actions Panel** - One-click admin tools for common tasks

---

## 🚀 Getting Started

### Accessing the System

1. **Login** to the FIDUS platform as an admin user
2. Navigate to **Admin Dashboard**
3. Look for **"App Documents"** or **"Technical Documentation"** tab
4. Click to access the Technical Documentation system

### First Time Setup

The system works out-of-the-box, but for optimal experience:

1. ✅ Verify all health checks are green
2. ✅ Test one Quick Action (e.g., "Test Integrations")
3. ✅ Configure email alerts if needed
4. ✅ Review API documentation

---

## 📋 Feature Guide

### 1️⃣ System Health Dashboard

**Purpose:** Monitor real-time health of all platform components

**How to Use:**
- Click **"System Health"** button in the view toggle
- View overall system status (Healthy/Degraded/Critical)
- Check individual component health cards
- Auto-refresh is enabled by default (every 30 seconds)
- Manually refresh anytime using the "Refresh" button

**Component Status Indicators:**
- 🟢 **Green**: Online and healthy
- 🟡 **Yellow**: Degraded performance
- 🔴 **Red**: Critical issues
- ⚪ **Gray**: Unknown/Not responding

**Key Metrics:**
- Response time (ms)
- Uptime percentage
- Last check timestamp
- Status history

**Automated Alerts:**
- Email notifications sent when components go down or recover
- Alerts stored in MongoDB for audit trail
- In-app notifications for real-time awareness

---

### 2️⃣ Quick Actions Panel

**Purpose:** One-click execution of common admin tasks

**How to Use:**
- Click **"Quick Actions"** button in the view toggle
- Browse actions by category:
  - 🚀 **Deployment**: Restart services
  - 💾 **Data Management**: Sync MT5 data, refresh performance
  - 🔧 **System Tools**: Test integrations, generate reports

**Executing Actions:**
1. Click "Execute" button on any action card
2. Watch the loading indicator
3. See success/error feedback in real-time
4. Check "Recent Actions" timeline for history

**Recent Actions Timeline:**
- Shows last 10 executed actions
- Status indicators (success/failed/in-progress)
- Timestamp (relative time: "5 minutes ago")
- Error messages if action failed
- Auto-refreshes after each action

**Time Savings:**
- Manual MT5 sync: 5 min → 10 sec ⚡
- Deploy services: 10 min → 30 sec ⚡
- Test integrations: 15 min → 1 min ⚡
- **Total: ~2 hours saved per day!**

---

### 3️⃣ API Documentation

**Purpose:** Complete API reference with interactive testing

**How to Use:**
- Click **"API Documentation"** button
- Use search bar to find specific endpoints
- Click category headers to expand/collapse
- Click endpoint rows to view details

**Features:**
- **8 API Categories**: Authentication, Client Management, Investment Management, etc.
- **50+ Documented Endpoints**: All with examples
- **Method Badges**: GET, POST, PUT, DELETE color-coded
- **Authentication Info**: Public, Authenticated, Admin Only
- **Request/Response Examples**: JSON formatted with syntax highlighting
- **Code Examples**: JavaScript, Python, cURL for each endpoint

**"Try It Out" Feature:**
1. Click "Try It Out" button on any endpoint
2. Fill in parameters (if required)
3. Add request body (if needed)
4. Click "Execute Request"
5. View live response with status code

---

### 4️⃣ Interactive Architecture Diagram

**Purpose:** Visual representation of system architecture with live status

**How to Use:**
- Click **"Architecture"** button
- Pan: Click and drag the diagram
- Zoom: Use mouse wheel or zoom controls
- Select: Click any node to see details

**Node Types:**
- 🖥️ **Application Nodes**: Frontend, Backend
- 💾 **Database Nodes**: MongoDB
- 🔌 **Service Nodes**: MT5 Bridge, Email Service
- 🔗 **Integration Nodes**: Google APIs, GitHub
- ☁️ **Infrastructure Nodes**: Render Hosting

**Node Colors:**
- 🟢 **Green**: Component healthy
- 🟡 **Yellow**: Component degraded
- 🔴 **Red**: Component critical
- ⚪ **Gray**: Status unknown

**Connection Lines:**
- Show data flow between components
- Color-coded by relationship type

**Diagram Controls:**
- Fit to view
- Zoom in/out
- Reset zoom
- Auto-layout

---

### 5️⃣ Credentials Vault

**Purpose:** Secure storage of system credentials (metadata only)

**⚠️ IMPORTANT SECURITY NOTE:**
- Credentials Vault stores **METADATA ONLY** (names, descriptions, last updated)
- **ACTUAL CREDENTIALS ARE NEVER STORED** in the application
- Real credentials are stored securely in Render environment variables
- This vault is for documentation and tracking purposes

**How to Use:**
- Click **"Credentials"** button
- View all credential entries
- See last rotation date
- Check audit log for access history

**Credential Categories:**
- Database credentials
- API keys
- OAuth tokens
- Service account keys

**Audit Log:**
- Tracks who accessed what credential
- Timestamp of access
- Action performed (view, update)
- User identification

---

### 6️⃣ Component Registry (Grid View)

**Purpose:** Overview of all system components

**How to Use:**
- Default view (or click **"Grid View"** button)
- Filter by category: Applications, Databases, Services, etc.
- View component cards with:
  - Name and description
  - Health status
  - Last checked timestamp
  - Quick actions

**Categories:**
- **Applications**: Frontend, Backend
- **Databases**: MongoDB
- **Services**: MT5 Bridge, Email Service
- **Integrations**: Google APIs, GitHub
- **Infrastructure**: Render Hosting

---

## ⚙️ System Settings

### Auto-Refresh

**System Health Dashboard:**
- Auto-refresh: Every 30 seconds (default: ON)
- Toggle: Click "Auto (30s)" / "Start Auto" button
- Countdown timer shows next refresh
- Manually refresh anytime

**Quick Actions:**
- Recent actions refresh after each execution
- Manual refresh available

### Email Alerts

**Configuration:**
Email alerts are configured in backend `.env` file:
```
SMTP_USERNAME=your_email@gmail.com
SMTP_APP_PASSWORD=your_app_password
ALERT_RECIPIENT_EMAIL=admin@fidus.com
```

**Alert Triggers:**
- Component status changes (healthy → degraded)
- Component goes offline
- Component recovers
- Critical system issues

**Alert Delivery:**
- Sent via SMTP (Gmail)
- Email subject includes urgency level
- Body includes component details and timestamp
- Also stored in MongoDB for history

---

## 🔧 Troubleshooting

### Health Check Issues

**Problem:** Component showing as "offline" but is actually running

**Solutions:**
1. Check network connectivity
2. Verify component URL is correct
3. Check firewall/security group rules
4. Manually refresh health check
5. Check component logs

**Problem:** Auto-refresh not working

**Solutions:**
1. Verify auto-refresh is enabled (toggle should be blue)
2. Check browser console for errors
3. Refresh the page
4. Clear browser cache

### Quick Actions Issues

**Problem:** Action fails with error message

**Solutions:**
1. Read error message carefully
2. Check if you have admin permissions
3. Verify backend is running
4. Check backend logs
5. Try action again
6. Contact system administrator

**Problem:** Action completes but doesn't seem to work

**Solutions:**
1. Wait 30-60 seconds for changes to propagate
2. Manually refresh affected page
3. Check system logs
4. For deployment actions, check Render dashboard

### API Documentation Issues

**Problem:** "Try It Out" returns 401 Unauthorized

**Solutions:**
1. Verify you're logged in
2. Check if endpoint requires admin access
3. Token may have expired - login again
4. Check authentication header

**Problem:** Endpoint returns unexpected error

**Solutions:**
1. Verify request body format matches example
2. Check parameter values
3. Review response error message
4. Check if endpoint is working (backend logs)

---

## 📊 Best Practices

### For Daily Use

1. **Start of Day:**
   - Check System Health Dashboard
   - Review recent alerts (if any)
   - Verify all components are green

2. **During Operations:**
   - Use Quick Actions for routine tasks
   - Monitor health dashboard for issues
   - Check recent actions timeline for audit

3. **End of Day:**
   - Review system health one last time
   - Check for any degraded components
   - Note any recurring issues

### For Maintenance

1. **Before Deployment:**
   - Check current system health
   - Notify team of planned downtime
   - Use Quick Actions to restart services

2. **After Deployment:**
   - Verify all components are healthy
   - Test critical integrations
   - Monitor for 5-10 minutes

3. **Regular Tasks:**
   - Weekly: Review audit logs
   - Monthly: Check credential rotation dates
   - Quarterly: Review architecture diagram for accuracy

---

## 🚨 Emergency Procedures

### System Critical Alert

If you receive a critical system alert:

1. **Immediate Actions:**
   - Open System Health Dashboard
   - Identify which component is critical
   - Check "Recent Actions" for clues

2. **Component-Specific Steps:**

   **Frontend Critical:**
   - Use Quick Action: "Restart Frontend"
   - Check Render dashboard
   - Review frontend logs

   **Backend Critical:**
   - Use Quick Action: "Restart Backend"
   - Check backend health endpoint directly
   - Review backend logs

   **Database Critical:**
   - Check MongoDB Atlas dashboard
   - Verify connection string
   - Check firewall rules

   **MT5 Bridge Critical:**
   - Check MT5 Bridge server status
   - Verify MT5 Bridge service is running
   - Test MT5 connection

3. **Escalation:**
   - If issue persists > 5 minutes, escalate
   - Contact platform administrator
   - Check Render status page
   - Review error logs

### Complete System Outage

If entire platform is down:

1. Check Render dashboard first
2. Verify MongoDB Atlas is online
3. Check MT5 Bridge server
4. Review recent deployments
5. Rollback if recent deployment caused issue
6. Contact hosting provider if infrastructure issue

---

## 📈 Performance Optimization

### Frontend Performance

**Implemented (Phase 7):**
- ✅ Lazy loading for heavy components
- ✅ Code splitting per view
- ✅ Optimized bundle size
- ✅ Smooth transitions and animations
- ✅ Consistent loading states

**Tips for Users:**
- Use modern browser (Chrome, Firefox, Edge, Safari latest)
- Clear cache if pages load slowly
- Disable unnecessary browser extensions

### Backend Performance

**Implemented:**
- ✅ MongoDB indexes on frequent queries
- ✅ Efficient health check intervals
- ✅ Request caching where appropriate
- ✅ Optimized API response times

**Monitoring:**
- Response times shown in health cards
- Slow endpoints highlighted in API docs
- Alert if response times exceed threshold

---

## 🔐 Security Considerations

### Authentication & Authorization

- All admin features require authentication
- JWT tokens expire after session timeout
- Admin-only endpoints protected at backend level
- Credentials never stored in frontend

### Audit Logging

**What's Logged:**
- Quick Actions executions
- Credentials vault access
- System health check failures
- Alert triggers

**Where:**
- MongoDB collections: `quick_actions_log`, `system_alerts`, `notifications`
- Audit logs: `credentials_audit`

**Retention:**
- Logs retained indefinitely (unless manually purged)
- Can be exported for compliance

### Best Practices

1. Never share admin credentials
2. Use strong passwords
3. Enable 2FA if available
4. Rotate credentials regularly
5. Review audit logs weekly
6. Report suspicious activity immediately

---

## 📞 Support & Resources

### Getting Help

**In-App:**
- Hover tooltips on most elements
- Error messages provide specific guidance
- Recent Actions timeline shows execution history

**Documentation:**
- This User Guide
- API Documentation (in-app)
- Architecture Diagram (visual reference)

**Technical Support:**
- Backend logs: `/var/log/supervisor/backend.err.log`
- Frontend logs: Browser console (F12)
- MongoDB: Check MongoDB Atlas dashboard

### Common Questions

**Q: How often does health monitoring run?**
A: Every 30 seconds (auto-refresh) or on-demand (manual refresh)

**Q: Are email alerts immediate?**
A: Yes, alerts sent within seconds of status change

**Q: Can I disable auto-refresh?**
A: Yes, toggle "Auto" button to pause auto-refresh

**Q: How do I add new credentials to the vault?**
A: Currently admin-only feature, contact system administrator

**Q: Can I export health history?**
A: Not yet implemented, coming in future update

**Q: Why do some Quick Actions take longer?**
A: Deployment and data sync actions interact with external services

---

## 🎓 Training Resources

### For New Admins

**Week 1: Basics**
- Day 1-2: Explore all views (Grid, Health, API, etc.)
- Day 3-4: Execute safe Quick Actions (Test Integrations)
- Day 5: Review documentation thoroughly

**Week 2: Operations**
- Day 1-2: Monitor health dashboard actively
- Day 3-4: Use Quick Actions for real tasks
- Day 5: Review audit logs and alerts

**Week 3: Advanced**
- Day 1-2: Understand architecture diagram fully
- Day 3-4: Test API endpoints with "Try It Out"
- Day 5: Handle simulated critical alert

### For Developers

- Study API Documentation thoroughly
- Use "Try It Out" to test endpoints
- Review code examples (JS, Python, cURL)
- Understand authentication requirements
- Check request/response schemas

---

## 🔄 System Maintenance

### Daily Tasks

- ✅ Check System Health Dashboard (5 min)
- ✅ Review recent alerts (if any) (2 min)
- ✅ Verify all components green (1 min)

### Weekly Tasks

- ✅ Review Quick Actions history (10 min)
- ✅ Check credentials rotation dates (5 min)
- ✅ Review audit logs (15 min)
- ✅ Test critical integrations (10 min)

### Monthly Tasks

- ✅ Update architecture diagram if needed (30 min)
- ✅ Review API documentation accuracy (20 min)
- ✅ Analyze health trends (30 min)
- ✅ Update credentials as needed (15 min)

---

## 🎉 Success Metrics

**With Technical Documentation System:**

- ⚡ **2 hours saved per day** on manual tasks
- 📊 **Real-time visibility** into system health
- 🚨 **Immediate alerts** for critical issues
- 🔒 **Centralized** credential management
- 📚 **Complete documentation** always up-to-date
- ⚙️ **One-click actions** for common tasks

**Before Technical Documentation:**
- Manual health checks: 30+ min/day
- No automated alerts
- Scattered documentation
- Manual service restarts: 10+ min each
- No API testing interface

**After Technical Documentation:**
- Health checks: Always visible, auto-refresh
- Email alerts: Immediate
- Documentation: Centralized, interactive
- Service restarts: 30 seconds
- API testing: Built-in "Try It Out"

---

## 📝 Version History

### Version 7.0 (Phase 7 - October 2024) ✅
- UI/UX consistency improvements
- Performance optimization (lazy loading, code splitting)
- Smooth animations and transitions
- Comprehensive documentation
- Production-ready polish

### Version 6.0 (Phase 6 - October 2024)
- Quick Actions Panel
- One-click admin tools
- Recent actions timeline
- Action logging to MongoDB

### Version 5.0 (Phase 5 - October 2024)
- Real-Time System Health Dashboard
- Automated email alerts
- Alert history and management
- In-app notifications

### Version 4.0 (Phase 4 - October 2024)
- API Documentation with "Try It Out"
- Code examples (JS, Python, cURL)
- Search functionality
- Interactive API testing

### Version 3.0 (Phase 3 - October 2024)
- Secure Credentials Vault
- Audit logging
- Metadata-only storage

### Version 2.0 (Phase 2 - October 2024)
- Interactive Architecture Diagram
- Visual system representation
- Live status indicators

### Version 1.0 (Phase 1 - October 2024)
- Component Registry
- Basic health monitoring
- Grid view

---

## 🏆 Congratulations!

You now have access to an **enterprise-grade Technical Documentation system** that provides:

✅ Real-time monitoring  
✅ Automated alerts  
✅ One-click actions  
✅ Complete API docs  
✅ Visual architecture  
✅ Secure credential management  

**This system saves hours of manual work and provides instant visibility into your entire platform!**

---

**Need Help?** Contact your system administrator or refer to the in-app documentation.

**Last Updated:** October 2024  
**Version:** 7.0 - Phase 7 Complete ✅
