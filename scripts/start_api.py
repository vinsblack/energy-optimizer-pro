"""
Start FastAPI server for Building Energy Optimizer.
"""
import uvicorn
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def start_api():
    """Start the FastAPI server."""
    print("🚀 Starting Building Energy Optimizer API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 ReDoc: http://localhost:8000/redoc")
    print("💾 Health Check: http://localhost:8000/")
    print("\n⚡ Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "api.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")

if __name__ == "__main__":
    start_api()
