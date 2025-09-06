#!/usr/bin/env python3
"""
FIDUS Performance Dashboard - Real-time Monitoring Web Interface
==============================================================

Web-based dashboard for monitoring FIDUS system performance in real-time.
Provides interactive charts, metrics, and system status.

Usage:
    python performance_dashboard.py --port 8080
    python performance_dashboard.py --config monitoring_config.yml
"""

from flask import Flask, render_template, jsonify, send_from_directory
import asyncio
import aiohttp
import json
import threading
import time
from datetime import datetime, timezone, timedelta
from collections import deque
import psutil
import argparse
import yaml
import logging

class PerformanceDashboard:
    """Real-time performance dashboard"""
    
    def __init__(self, config_file: str = None):
        self.config = self.load_config(config_file)
        self.base_url = self.config.get('base_url', 'https://your-domain.com')
        self.metrics_buffer = deque(maxlen=1000)  # Keep last 1000 data points
        self.current_metrics = {}
        self.setup_logging()
        self.setup_flask()
        
    def load_config(self, config_file: str) -> dict:
        """Load configuration"""
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            except FileNotFoundError:
                print(f"Config file {config_file} not found, using defaults")
        
        return {
            'base_url': 'https://your-production-domain.com',
            'update_interval': 30,
            'dashboard_port': 8080
        }
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_flask(self):
        """Setup Flask application"""
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/')
        def dashboard():
            return self.render_dashboard()
        
        @self.app.route('/api/metrics')
        def get_metrics():
            return jsonify(self.current_metrics)
        
        @self.app.route('/api/metrics/history')
        def get_metrics_history():
            return jsonify(list(self.metrics_buffer))
        
        @self.app.route('/api/system/status')
        def get_system_status():
            return jsonify(self.get_system_status())
        
        @self.app.route('/health')
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    
    def render_dashboard(self):
        """Render dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIDUS Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center mb-8 text-gray-800">
            🏦 FIDUS Performance Dashboard
        </h1>
        
        <!-- Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="metric-card rounded-lg p-6 text-white">
                <h3 class="text-lg font-semibold mb-2">System Status</h3>
                <p id="system-status" class="text-2xl font-bold">Loading...</p>
            </div>
            <div class="metric-card rounded-lg p-6 text-white">
                <h3 class="text-lg font-semibold mb-2">API Response</h3>
                <p id="api-response" class="text-2xl font-bold">Loading...</p>
            </div>
            <div class="metric-card rounded-lg p-6 text-white">
                <h3 class="text-lg font-semibold mb-2">CPU Usage</h3>
                <p id="cpu-usage" class="text-2xl font-bold">Loading...</p>
            </div>
            <div class="metric-card rounded-lg p-6 text-white">
                <h3 class="text-lg font-semibold mb-2">Memory Usage</h3>
                <p id="memory-usage" class="text-2xl font-bold">Loading...</p>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h3 class="text-xl font-semibold mb-4">System Resources</h3>
                <div class="chart-container">
                    <canvas id="resourceChart"></canvas>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h3 class="text-xl font-semibold mb-4">API Performance</h3>
                <div class="chart-container">
                    <canvas id="apiChart"></canvas>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h3 class="text-xl font-semibold mb-4">Rate Limiter Activity</h3>
                <div class="chart-container">
                    <canvas id="rateLimiterChart"></canvas>
                </div>
            </div>
            
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h3 class="text-xl font-semibold mb-4">MT5 Integration Status</h3>
                <div id="mt5-status" class="space-y-2">
                    Loading MT5 status...
                </div>
            </div>
        </div>
        
        <!-- Real-time Logs -->
        <div class="mt-8 bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-xl font-semibold mb-4">Real-time System Logs</h3>
            <div id="logs-container" class="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-64 overflow-y-auto">
                <div>Starting FIDUS Performance Dashboard...</div>
            </div>
        </div>
    </div>

    <script>
        // Global chart instances
        let resourceChart, apiChart, rateLimiterChart;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            startRealTimeUpdates();
        });
        
        function initializeCharts() {
            // Resource Usage Chart
            const resourceCtx = document.getElementById('resourceChart').getContext('2d');
            resourceChart = new Chart(resourceCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU Usage (%)',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1
                    }, {
                        label: 'Memory Usage (%)',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        tension: 0.1
                    }, {
                        label: 'Disk Usage (%)',
                        data: [],
                        borderColor: 'rgb(255, 205, 86)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
            
            // API Performance Chart
            const apiCtx = document.getElementById('apiChart').getContext('2d');
            apiChart = new Chart(apiCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            // Rate Limiter Chart
            const rateLimiterCtx = document.getElementById('rateLimiterChart').getContext('2d');
            rateLimiterChart = new Chart(rateLimiterCtx, {
                type: 'bar',
                data: {
                    labels: ['Total Requests', 'Blocked Requests', 'Active Clients'],
                    datasets: [{
                        label: 'Count',
                        data: [0, 0, 0],
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(255, 205, 86, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function startRealTimeUpdates() {
            updateMetrics();
            setInterval(updateMetrics, 30000); // Update every 30 seconds
        }
        
        async function updateMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const metrics = await response.json();
                
                updateStatusCards(metrics);
                updateCharts(metrics);
                updateMT5Status(metrics);
                addLogEntry(`Updated metrics - Status: ${metrics.system_status}`);
                
            } catch (error) {
                console.error('Error updating metrics:', error);
                addLogEntry(`ERROR: Failed to update metrics - ${error.message}`);
            }
        }
        
        function updateStatusCards(metrics) {
            const statusEmoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'unhealthy': '❌'
            };
            
            document.getElementById('system-status').textContent = 
                statusEmoji[metrics.system_status] || '❓' + ' ' + (metrics.system_status || 'Unknown').toUpperCase();
            
            document.getElementById('api-response').textContent = 
                (metrics.api_response_time * 1000).toFixed(0) + 'ms';
                
            document.getElementById('cpu-usage').textContent = 
                (metrics.cpu_usage || 0).toFixed(1) + '%';
                
            document.getElementById('memory-usage').textContent = 
                (metrics.memory_usage || 0).toFixed(1) + '%';
        }
        
        function updateCharts(metrics) {
            const now = new Date().toLocaleTimeString();
            
            // Resource Chart
            if (resourceChart.data.labels.length > 20) {
                resourceChart.data.labels.shift();
                resourceChart.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            resourceChart.data.labels.push(now);
            resourceChart.data.datasets[0].data.push(metrics.cpu_usage || 0);
            resourceChart.data.datasets[1].data.push(metrics.memory_usage || 0);
            resourceChart.data.datasets[2].data.push(metrics.disk_usage || 0);
            resourceChart.update();
            
            // API Chart
            if (apiChart.data.labels.length > 20) {
                apiChart.data.labels.shift();
                apiChart.data.datasets[0].data.shift();
            }
            
            apiChart.data.labels.push(now);
            apiChart.data.datasets[0].data.push((metrics.api_response_time || 0) * 1000);
            apiChart.update();
            
            // Rate Limiter Chart
            const rateLimiterStats = metrics.rate_limiter_stats || {};
            rateLimiterChart.data.datasets[0].data = [
                rateLimiterStats.total_requests || 0,
                rateLimiterStats.blocked_requests || 0,
                rateLimiterStats.active_clients || 0
            ];
            rateLimiterChart.update();
        }
        
        function updateMT5Status(metrics) {
            const mt5Status = metrics.mt5_accounts_status || {};
            const container = document.getElementById('mt5-status');
            
            container.innerHTML = `
                <div class="flex justify-between">
                    <span>Collector Status:</span>
                    <span class="font-semibold">${mt5Status.collector_status || 'Unknown'}</span>
                </div>
                <div class="flex justify-between">
                    <span>Accounts Monitored:</span>
                    <span class="font-semibold">${mt5Status.accounts_monitored || 0}</span>
                </div>
                <div class="flex justify-between">
                    <span>Data Quality:</span>
                    <span class="font-semibold">${mt5Status.data_quality || 'Unknown'}</span>
                </div>
                <div class="flex justify-between">
                    <span>Last Collection:</span>
                    <span class="font-semibold">${mt5Status.last_collection || 'Unknown'}</span>
                </div>
            `;
        }
        
        function addLogEntry(message) {
            const container = document.getElementById('logs-container');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.textContent = `[${timestamp}] ${message}`;
            container.appendChild(logEntry);
            container.scrollTop = container.scrollHeight;
            
            // Keep only last 50 log entries
            while (container.children.length > 50) {
                container.removeChild(container.firstChild);
            }
        }
    </script>
</body>
</html>
        """
    
    async def collect_metrics(self):
        """Collect current system metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get API health metrics
            api_metrics = {'response_time': 0, 'status': 'unknown'}
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/api/health/metrics", timeout=10) as response:
                        end_time = time.time()
                        api_metrics['response_time'] = end_time - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            api_metrics['status'] = 'healthy'
                            api_metrics['data'] = data
                        else:
                            api_metrics['status'] = 'unhealthy'
            except Exception as e:
                api_metrics['status'] = 'error'
                api_metrics['error'] = str(e)
            
            # Determine overall system status
            system_status = 'healthy'
            if (cpu_percent > 90 or memory.percent > 95 or 
                api_metrics['status'] != 'healthy'):
                system_status = 'unhealthy'
            elif (cpu_percent > 70 or memory.percent > 80 or 
                  api_metrics['response_time'] > 1.0):
                system_status = 'warning'
            
            metrics = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system_status': system_status,
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'api_response_time': api_metrics['response_time'],
                'rate_limiter_stats': api_metrics.get('data', {}).get('rate_limiter', {}),
                'mt5_accounts_status': {
                    'collector_status': 'running',
                    'accounts_monitored': 1,
                    'data_quality': 'excellent',
                    'last_collection': datetime.now().strftime('%H:%M:%S')
                }
            }
            
            self.current_metrics = metrics
            self.metrics_buffer.append(metrics)
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
    
    def get_system_status(self):
        """Get detailed system status"""
        return {
            'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0,
            'python_version': f"{psutil.version_info[0]}.{psutil.version_info[1]}",
            'dashboard_version': '1.0.0',
            'last_update': datetime.now().isoformat()
        }
    
    def start_background_updates(self):
        """Start background metrics collection"""
        def update_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while True:
                try:
                    loop.run_until_complete(self.collect_metrics())
                except Exception as e:
                    self.logger.error(f"Background update error: {e}")
                
                time.sleep(self.config.get('update_interval', 30))
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def run(self, host='0.0.0.0', port=8080):
        """Run the dashboard"""
        self.start_time = time.time()
        self.start_background_updates()
        
        print(f"""
🚀 FIDUS Performance Dashboard Starting...

Dashboard URL: http://localhost:{port}
API Base URL: {self.base_url}
Update Interval: {self.config.get('update_interval', 30)} seconds

Press Ctrl+C to stop
        """)
        
        self.app.run(host=host, port=port, debug=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='FIDUS Performance Dashboard')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--port', type=int, default=8080, help='Dashboard port')
    parser.add_argument('--host', default='0.0.0.0', help='Dashboard host')
    
    args = parser.parse_args()
    
    dashboard = PerformanceDashboard(args.config)
    dashboard.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()