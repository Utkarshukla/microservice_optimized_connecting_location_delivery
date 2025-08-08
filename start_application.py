#!/usr/bin/env python3
"""
Startup script for the Delivery Route Optimization System.
This script starts both the Python and Node.js backends.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class ApplicationStarter:
    def __init__(self):
        self.processes = []
        self.running = True
        self.original_dir = os.getcwd()
        
    def start_python_backend(self):
        """Start the Python FastAPI backend."""
        print("🚀 Starting Python backend...")
        try:
            # Get absolute path to python_backend directory
            python_backend_dir = os.path.join(self.original_dir, "python_backend")
            
            # Install dependencies if requirements.txt exists
            requirements_file = os.path.join(python_backend_dir, "requirements.txt")
            if os.path.exists(requirements_file):
                print("📦 Installing Python dependencies...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], 
                             check=True, capture_output=True, cwd=python_backend_dir)
            
            # Start the Python server
            start_server_file = os.path.join(python_backend_dir, "start_server.py")
            process = subprocess.Popen([sys.executable, start_server_file],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True,
                                     cwd=python_backend_dir)
            
            self.processes.append(("Python Backend", process))
            print("✅ Python backend started successfully!")
            
        except Exception as e:
            print(f"❌ Failed to start Python backend: {e}")
            return False
        return True
    
    def start_node_backend(self):
        """Start the Node.js Express backend."""
        print("🚀 Starting Node.js backend...")
        try:
            # Get absolute path to node_backend directory
            node_backend_dir = os.path.join(self.original_dir, "node_backend")
            
            # Check if node_modules exists (dependencies already installed)
            node_modules_dir = os.path.join(node_backend_dir, "node_modules")
            if not os.path.exists(node_modules_dir):
                print("📦 Installing Node.js dependencies...")
                subprocess.run(["npm", "install"], check=True, capture_output=True, cwd=node_backend_dir)
            else:
                print("📦 Node.js dependencies already installed")
            
            # Start the Node.js server directly with node
            server_file = os.path.join(node_backend_dir, "server.js")
            process = subprocess.Popen(["node", server_file],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True,
                                     cwd=node_backend_dir)
            
            self.processes.append(("Node.js Backend", process))
            print("✅ Node.js backend started successfully!")
            
        except Exception as e:
            print(f"❌ Failed to start Node.js backend: {e}")
            return False
        return True
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed."""
        while self.running:
            for name, process in self.processes:
                if process.poll() is not None:
                    print(f"⚠️ {name} has stopped unexpectedly")
                    # Could implement restart logic here
            time.sleep(5)
    
    def stop_all(self):
        """Stop all running processes."""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        for name, process in self.processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️ Force killing {name}")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n📡 Received signal {signum}")
        self.stop_all()
        sys.exit(0)
    
    def run(self):
        """Main method to start the application."""
        print("🚚 Delivery Route Optimization System")
        print("=" * 50)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start Python backend
            if not self.start_python_backend():
                print("❌ Failed to start Python backend. Exiting.")
                return False
            
            # Start Node.js backend
            if not self.start_node_backend():
                print("❌ Failed to start Node.js backend. Exiting.")
                return False
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()
            
            print("\n🎉 Application started successfully!")
            print("=" * 50)
            print("📊 Services:")
            print("  • Python Backend: http://localhost:8000")
            print("  • Node.js Gateway: http://localhost:3000")
            print("  • Web Interface: Open index.html in your browser")
            print("  • API Documentation: http://localhost:8000/docs")
            print("\n💡 Press Ctrl+C to stop all services")
            print("=" * 50)
            
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n📡 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            self.stop_all()
        
        return True

def main():
    """Main entry point."""
    starter = ApplicationStarter()
    success = starter.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 