#!/bin/bash

echo "========================================"
echo "  🚚 Delivery Route Optimization System"
echo "========================================"
echo ""
echo "Starting the application..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    echo "Please install Node.js 14+ from https://nodejs.org"
    exit 1
fi

echo "✅ Python and Node.js found"
echo ""

# Start the application
echo "🚀 Starting both backends..."
python3 start_application.py

echo ""
echo "========================================"
echo "  Application stopped"
echo "========================================"
