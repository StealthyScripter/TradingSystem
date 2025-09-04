#!/usr/bin/env python3
"""
Simple script to toggle authentication on/off
"""

import os
import sys
from pathlib import Path

def update_env_file(disable_auth: bool):
    """Update .env file with DISABLE_AUTH setting"""

    env_file = Path(".env")

    if not env_file.exists():
        print("❌ .env file not found")
        print("   Create .env file first with your settings")
        return False

    # Read current content
    with open(env_file, 'r') as f:
        lines = f.readlines()

    # Update or add DISABLE_AUTH line
    auth_line = f"DISABLE_AUTH={str(disable_auth).lower()}\n"
    auth_found = False

    for i, line in enumerate(lines):
        if line.startswith("DISABLE_AUTH="):
            lines[i] = auth_line
            auth_found = True
            break

    if not auth_found:
        lines.append(auth_line)

    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)

    return True

def main():
    """Main toggle function"""

    if len(sys.argv) != 2 or sys.argv[1] not in ['on', 'off', 'status']:
        print("Usage: python toggle_auth.py [on|off|status]")
        print("")
        print("Commands:")
        print("  on     - Enable authentication (DISABLE_AUTH=false)")
        print("  off    - Disable authentication (DISABLE_AUTH=true)")
        print("  status - Show current authentication status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        # Show current status
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()

            if "DISABLE_AUTH=true" in content:
                print("🔓 Authentication is currently DISABLED")
                print("   API will use mock user for all requests")
            elif "DISABLE_AUTH=false" in content:
                print("🔒 Authentication is currently ENABLED")
                print("   API requires valid Clerk JWT tokens")
            else:
                print("🤷 DISABLE_AUTH not found in .env")
                print("   Authentication is probably ENABLED (default)")
        else:
            print("❌ .env file not found")

    elif command == "off":
        # Disable authentication
        if update_env_file(True):
            print("🔓 Authentication DISABLED")
            print("   Updated .env file: DISABLE_AUTH=true")
            print("   Restart the server to apply changes: python run.py")

    elif command == "on":
        # Enable authentication
        if update_env_file(False):
            print("🔒 Authentication ENABLED")
            print("   Updated .env file: DISABLE_AUTH=false")
            print("   Restart the server to apply changes: python run.py")
            print("   Make sure you have valid Clerk configuration!")

if __name__ == "__main__":
    main()