#!/usr/bin/env python3
"""
VME Textual CLI Client Launcher
Simple wrapper to launch the client with proper environment setup
"""

import os
import sys
from pathlib import Path

def load_dotenv_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

def main():
    """Launch the VME Textual CLI Client"""
    
    load_dotenv_file()
    
    # Check for API key (after loading .env)
    if not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("❌ API key required: ANTHROPIC_API_KEY or OPENAI_API_KEY")
        print("   Add to .env file or set environment variable:")
        print("   ANTHROPIC_API_KEY=your_key")
        print("   OPENAI_API_KEY=your_key") 
        sys.exit(1)
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print("🚀 Launching VME Infrastructure Chat Client...")
    print("   Press Ctrl+C or Ctrl+Q to quit")
    print()
    
    try:
        # Import and run the client
        from src.clients.textual_cli.main import main as client_main
        client_main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        # Cleanup any hanging processes
        import subprocess
        try:
            subprocess.run(['pkill', '-f', 'vme.*server.*py'], check=False, timeout=2)
        except:
            pass

if __name__ == '__main__':
    main()