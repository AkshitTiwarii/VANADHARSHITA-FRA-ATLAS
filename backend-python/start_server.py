#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting FRA Atlas API...")
    try:
        uvicorn.run(app, host="127.0.0.1", port=3001, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)