"""
Start Streamlit dashboard for Building Energy Optimizer.
"""
import subprocess
import sys
import os

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("📊 Starting Building Energy Optimizer Dashboard...")
    print("🌐 Dashboard URL: http://localhost:8501")
    print("⚡ Press Ctrl+C to stop the dashboard")
    
    # Get dashboard path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dashboard_path = os.path.join(project_root, "dashboard", "app.py")
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")

if __name__ == "__main__":
    start_dashboard()
