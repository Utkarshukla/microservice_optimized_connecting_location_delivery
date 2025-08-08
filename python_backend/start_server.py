#!/usr/bin/env python3
import uvicorn
import logging
from config import DEFAULT_API_CONFIG

def main():
    """Start the FastAPI server."""
    print(f"Starting Delivery Route Optimization API server...")
    print(f"Host: {DEFAULT_API_CONFIG.host}")
    print(f"Port: {DEFAULT_API_CONFIG.port}")
    print(f"Debug mode: {DEFAULT_API_CONFIG.debug}")
    print(f"API Documentation: http://{DEFAULT_API_CONFIG.host}:{DEFAULT_API_CONFIG.port}/docs")
    
    uvicorn.run(
        "main:app",
        host=DEFAULT_API_CONFIG.host,
        port=DEFAULT_API_CONFIG.port,
        reload=DEFAULT_API_CONFIG.debug,
        log_level="info"
    )

if __name__ == "__main__":
    main() 