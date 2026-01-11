#!/bin/bash
# ============================================================
# VIKING MT4 Bridge Service Startup Script (Linux/Mac)
# ============================================================
# This script starts the VIKING MT4 bridge service on port 8001
# Completely separate from FIDUS MT5 bridge (port 8000)
# ============================================================

echo ""
echo "============================================================"
echo "   VIKING MT4 Bridge Service"
echo "   Port: 8001"
echo "   Account: 33627673 (MEXAtlantic)"
echo "============================================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Creating template .env file..."
    cat > .env << EOF
MONGO_URL=your_mongodb_connection_string_here
DB_NAME=fidus_production
VIKING_BRIDGE_PORT=8001
EOF
    echo "Please edit .env file with your MongoDB connection string"
    exit 1
fi

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q fastapi uvicorn motor python-dotenv pydantic

# Start the service
echo ""
echo "Starting VIKING MT4 Bridge Service..."
echo ""
python viking_mt4_bridge_service.py
