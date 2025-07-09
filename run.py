#!/usr/bin/env python3
"""
Simple startup script for Cal Pulse Dashboard
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit application"""
    print("🚀 Starting Cal Pulse Dashboard...")
    print("📅 Your calendar productivity insights await!")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: Please run this script from the cal-pulse-dashboard directory")
        print("📁 Current directory:", os.getcwd())
        return 1
    
    # Run streamlit
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Cal Pulse Dashboard!")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())