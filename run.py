#!/usr/bin/env python3
"""
Investment Portfolio Full Stack Startup Script
Cross-platform Python script to run both FastAPI backend and Next.js frontend
"""

import os
import sys
import subprocess
import time
import threading
import signal
import webbrowser
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    END = '\033[0m'


class PortfolioRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "flexpesa-ai"
        self.frontend_dir = self.root_dir / "flexpesa-client"

    def print_header(self):
        """Print startup header"""
        header = f"""
{Colors.BLUE}╔══════════════════════════════════════════════════════════════╗
║                 Investment Portfolio MVP                     ║
║              FastAPI + Next.js Full Stack                   ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
"""
        print(header)

    def log(self, message, color=Colors.GREEN):
        """Print colored log message"""
        print(f"{color}[INFO]{Colors.END} {message}")

    def warn(self, message):
        """Print warning message"""
        print(f"{Colors.YELLOW}[WARN]{Colors.END} {message}")

    def error(self, message):
        """Print error message"""
        print(f"{Colors.RED}[ERROR]{Colors.END} {message}")

    def command_exists(self, command):
        """Check if a command exists in PATH"""
        try:
            subprocess.run([command, "--version"],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_prerequisites(self):
        """Check if required tools are installed"""
        self.log("Checking prerequisites...")

        # Check Python
        if not self.command_exists("python") and not self.command_exists("python3"):
            self.error("Python is not installed. Please install Python 3.8+ and try again.")
            return False

        # Check Node.js
        if not self.command_exists("node"):
            self.error("Node.js is not installed. Please install Node.js 18+ and try again.")
            return False

        # Check npm
        if not self.command_exists("npm"):
            self.error("npm is not installed. Please install npm and try again.")
            return False

        self.log("✅ All prerequisites found")
        return True

    def get_python_cmd(self):
        """Get the correct Python command"""
        if self.command_exists("python3"):
            return "python3"
        return "python"

    def setup_backend(self):
        """Setup FastAPI backend"""
        self.log("Setting up FastAPI backend...")

        # Change to backend directory
        os.chdir(self.backend_dir)

        python_cmd = self.get_python_cmd()

        # Create virtual environment if it doesn't exist
        venv_dir = self.backend_dir / "venv"
        if not venv_dir.exists():
            self.log("Creating Python virtual environment...")
            subprocess.run([python_cmd, "-m", "venv", "venv"], check=True)

        # Get activation script path
        if os.name == 'nt':  # Windows
            activate_script = venv_dir / "Scripts" / "activate.bat"
            pip_cmd = venv_dir / "Scripts" / "pip"
            python_venv = venv_dir / "Scripts" / "python"
        else:  # Unix/Linux/Mac
            activate_script = venv_dir / "bin" / "activate"
            pip_cmd = venv_dir / "bin" / "pip"
            python_venv = venv_dir / "bin" / "python"

        # Install dependencies
        self.log("Installing Python dependencies...")
        subprocess.run([str(pip_cmd), "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_cmd), "install", "-r", "requirements.txt"], check=True)

        # Create data directory
        data_dir = self.backend_dir / "data"
        data_dir.mkdir(exist_ok=True)

        # Initialize database
        self.log("Initializing database with sample data...")
        subprocess.run([str(python_venv), "scripts/init_data.py"], check=True)

        self.log("✅ Backend setup complete")
        return python_venv

    def setup_frontend(self):
        """Setup Next.js frontend"""
        self.log("Setting up Next.js frontend...")

        # Change to frontend directory
        os.chdir(self.frontend_dir)

        # Install Node.js dependencies
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            self.log("Installing Node.js dependencies...")
            subprocess.run(["npm", "install"], check=True)
        else:
            self.log("Node.js dependencies already installed")

        self.log("✅ Frontend setup complete")

    def start_backend(self, python_venv):
        """Start FastAPI backend in a separate process"""
        self.log("🚀 Starting FastAPI backend on http://localhost:8000")

        os.chdir(self.backend_dir)

        try:
            self.backend_process = subprocess.Popen(
                [str(python_venv), "run.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Start thread to handle backend output
            backend_thread = threading.Thread(
                target=self._handle_output,
                args=(self.backend_process, "BACKEND"),
                daemon=True
            )
            backend_thread.start()

        except Exception as e:
            self.error(f"Failed to start backend: {e}")
            return False

        return True

    def start_frontend(self):
        """Start Next.js frontend in a separate process"""
        self.log("🚀 Starting Next.js frontend on http://localhost:3000")

        os.chdir(self.frontend_dir)

        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Start thread to handle frontend output
            frontend_thread = threading.Thread(
                target=self._handle_output,
                args=(self.frontend_process, "FRONTEND"),
                daemon=True
            )
            frontend_thread.start()

        except Exception as e:
            self.error(f"Failed to start frontend: {e}")
            return False

        return True

    def _handle_output(self, process, service_name):
        """Handle output from backend/frontend processes"""
        color = Colors.CYAN if service_name == "BACKEND" else Colors.PURPLE

        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"{color}[{service_name}]{Colors.END} {line.strip()}")

    def open_browser(self):
        """Open browser to frontend URL"""
        try:
            self.log("Opening browser...")
            time.sleep(2)
            webbrowser.open("http://localhost:3000")
        except Exception as e:
            self.warn(f"Could not open browser: {e}")

    def print_status(self):
        """Print running status"""
        status = f"""
{Colors.GREEN}
╔══════════════════════════════════════════════════════════════╗
║                     🎉 SERVICES RUNNING                      ║
╠══════════════════════════════════════════════════════════════╣
║  📱 Frontend (Next.js):  http://localhost:3000               ║
║  🔧 Backend API (FastAPI): http://localhost:8000             ║
║  📊 API Documentation:   http://localhost:8000/docs          ║
║                                                              ║
║  🛑 Press Ctrl+C to stop all services                        ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(status)

    def cleanup(self):
        """Clean up processes on exit"""
        self.log("Shutting down services...")

        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()

        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()

    def run(self):
        """Main run method"""
        try:
            self.print_header()

            # Check prerequisites
            if not self.check_prerequisites():
                return 1

            # Setup backend
            python_venv = self.setup_backend()

            # Setup frontend
            self.setup_frontend()

            # Start backend
            if not self.start_backend(python_venv):
                return 1

            # Wait for backend to start
            time.sleep(3)

            # Start frontend
            if not self.start_frontend():
                return 1

            # Wait for frontend to start
            time.sleep(5)

            # Print status
            self.print_status()

            # Open browser
            self.open_browser()

            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)

                    # Check if processes are still running
                    if self.backend_process and self.backend_process.poll() is not None:
                        self.error("Backend process stopped unexpectedly")
                        break

                    if self.frontend_process and self.frontend_process.poll() is not None:
                        self.error("Frontend process stopped unexpectedly")
                        break

            except KeyboardInterrupt:
                self.log("Received interrupt signal")

        except Exception as e:
            self.error(f"Unexpected error: {e}")
            return 1

        finally:
            self.cleanup()

        return 0


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\nReceived interrupt signal, shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    # Run the application
    runner = PortfolioRunner()
    exit_code = runner.run()
    sys.exit(exit_code)
