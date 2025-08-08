# 🚚 Delivery Route Optimization System - Command Guide

This guide provides all the commands needed to set up and run the delivery routing system.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** with pip
- **Node.js 14+** with npm
- **Git** (for version control)

### Check Versions
```bash
python --version
node --version
npm --version
git --version
```

## 🚀 Quick Start (All-in-One)

### Option 1: Automated Startup (Recommended)
```bash
# Start both Python and Node.js backends automatically
python start_application.py
```

### Option 2: Manual Startup
```bash
# Terminal 1: Start Python Backend
cd python_backend
python main.py

# Terminal 2: Start Node.js Backend  
cd node_backend
npm install
node server.js
```

## 📦 Installation Commands

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd Route-mapping
```

### 2. Install Python Dependencies
```bash
cd python_backend
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies
```bash
cd node_backend
npm install
```

## 🔧 Development Commands

### Python Backend
```bash
# Navigate to Python backend
cd python_backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py

# Run with auto-reload (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test the API
curl http://127.0.0.1:8000/health

# Get example data
curl http://127.0.0.1:8000/example-data

# Test route optimization
curl -X POST http://127.0.0.1:8000/optimize-route \
  -H "Content-Type: application/json" \
  -d @example_request.json

# Generate visualizations
curl -X POST http://127.0.0.1:8000/generate-visualizations \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

### Node.js Backend
```bash
# Navigate to Node.js backend
cd node_backend

# Install dependencies
npm install

# Run the server
node server.js

# Run with auto-reload (development)
npm run dev

# Test the API
curl http://localhost:3000/api/health

# Test route optimization through gateway
curl -X POST http://localhost:3000/api/optimize-route \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

## 🧪 Testing Commands

### Run All Tests
```bash
# Run comprehensive test suite
python test_application.py
```

### Test Individual Components
```bash
# Test Python backend only
python -c "
import sys
sys.path.append('python_backend')
from routing_engine import RoutingEngine
engine = RoutingEngine()
print('✅ Python backend test successful')
"

# Test Node.js backend
curl http://localhost:3000/api/health

# Test visualization generation
curl -X POST http://127.0.0.1:8000/generate-visualizations \
  -H "Content-Type: application/json" \
  -d '{
    "pickup": {
      "address": "Warehouse, Mumbai",
      "zipcode": "400001",
      "lat": 18.9356,
      "lng": 72.8376,
      "start_time": "09:00",
      "end_time": "18:00"
    },
    "settings": {
      "return_to_origin": true,
      "time_per_stop_minutes": 10,
      "vehicle_speed_kmph": 40.0,
      "optimize_by": "priority"
    },
    "deliveries": [
      {
        "address": "Client A",
        "zipcode": "400020",
        "lat": 18.9447,
        "lng": 72.8235,
        "priority": 1,
        "time_window": {
          "start": "10:00",
          "end": "13:00"
        }
      }
    ]
  }'
```

## 🌐 Web Interface

### Open Web Interface
```bash
# Open the HTML interface in your browser
start index.html  # Windows
open index.html   # macOS
xdg-open index.html  # Linux
```

### Access API Documentation
```bash
# Python backend API docs
start http://127.0.0.1:8000/docs

# Node.js backend health
start http://localhost:3000/api/health
```

## 📊 Visualization Commands

### Generate Visualizations
```bash
# Generate interactive map and charts
curl -X POST http://127.0.0.1:8000/generate-visualizations \
  -H "Content-Type: application/json" \
  -d @your_request.json

# View generated visualizations
start http://127.0.0.1:8000/visualizations/route_map.html
start http://127.0.0.1:8000/visualizations/route_summary.png
start http://127.0.0.1:8000/visualizations/route_timeline.png
```

## 🔍 Debugging Commands

### Check Service Status
```bash
# Check if Python backend is running
curl http://127.0.0.1:8000/health

# Check if Node.js backend is running
curl http://localhost:3000/api/health

# Check running processes
tasklist | findstr python  # Windows
ps aux | grep python       # Linux/macOS
```

### View Logs
```bash
# Python backend logs (if running in terminal)
# Check the terminal where python main.py is running

# Node.js backend logs (if running in terminal)
# Check the terminal where node server.js is running
```

### Debug Route Optimization
```bash
# Get detailed debug information
curl -X POST http://127.0.0.1:8000/debug-route \
  -H "Content-Type: application/json" \
  -d @your_request.json
```

## 🛠️ Maintenance Commands

### Update Dependencies
```bash
# Update Python dependencies
cd python_backend
pip install --upgrade -r requirements.txt

# Update Node.js dependencies
cd node_backend
npm update
```

### Clean Up
```bash
# Remove generated files
del route_map.html route_summary.png route_timeline.png  # Windows
rm route_map.html route_summary.png route_timeline.png   # Linux/macOS

# Remove Python cache
del /s *.pyc  # Windows
find . -name "*.pyc" -delete  # Linux/macOS

# Remove Node.js cache
cd node_backend
rm -rf node_modules
npm install
```

## 🚨 Troubleshooting Commands

### Port Conflicts
```bash
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/macOS

# Check what's using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/macOS

# Kill process by PID
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/macOS
```

### Permission Issues
```bash
# Windows: Run as Administrator
# Linux/macOS: Use sudo if needed
sudo python main.py
```

### Dependency Issues
```bash
# Reinstall Python dependencies
cd python_backend
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Reinstall Node.js dependencies
cd node_backend
rm -rf node_modules package-lock.json
npm install
```

## 📝 Example Request Files

### Create example_request.json
```bash
echo '{
  "pickup": {
    "address": "Warehouse, Mumbai",
    "zipcode": "400001",
    "lat": 18.9356,
    "lng": 72.8376,
    "start_time": "09:00",
    "end_time": "18:00"
  },
  "settings": {
    "return_to_origin": true,
    "time_per_stop_minutes": 10,
    "vehicle_speed_kmph": 40.0,
    "optimize_by": "priority"
  },
  "deliveries": [
    {
      "address": "Client A",
      "zipcode": "400020",
      "lat": 18.9447,
      "lng": 72.8235,
      "priority": 1,
      "time_window": {
        "start": "10:00",
        "end": "13:00"
      }
    }
  ]
}' > example_request.json
```

## 🎯 Production Deployment

### Environment Variables
```bash
# Create .env file for Python backend
cd python_backend
echo "MAX_TRAVEL_TIME_HOURS=4.0" > .env
echo "DEFAULT_SPEED_KMH=50.0" >> .env
echo "HIGH_PRIORITY_WEIGHT=1000.0" >> .env

# Create .env file for Node.js backend
cd ../node_backend
echo "PORT=3000" > .env
echo "PYTHON_API_URL=http://127.0.0.1:8000" >> .env
echo "NODE_ENV=production" >> .env
```

### Production Startup
```bash
# Use PM2 for Node.js (install globally first: npm install -g pm2)
cd node_backend
pm2 start server.js --name "route-optimizer-api"

# Use systemd for Python (Linux)
sudo systemctl enable route-optimizer-python
sudo systemctl start route-optimizer-python
```

## 📚 Additional Resources

- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Example Data**: http://127.0.0.1:8000/example-data
- **Configuration**: http://127.0.0.1:8000/config

## 🆘 Emergency Commands

### Stop All Services
```bash
# Stop Python backend (Ctrl+C in terminal)
# Stop Node.js backend (Ctrl+C in terminal)

# Or kill all Python processes
taskkill /f /im python.exe  # Windows
pkill -f python             # Linux/macOS

# Or kill all Node.js processes
taskkill /f /im node.exe    # Windows
pkill -f node               # Linux/macOS
```

### Reset Everything
```bash
# Stop all services
# Delete generated files
# Restart from scratch
python start_application.py
```

---

**💡 Tip**: Save this file as `cmd.md` in your project root for quick reference!
