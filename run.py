#!/usr/bin/env python3
"""
FlexPesa Portfolio - Full Stack Development Runner
Automatically sets up and runs both backend and frontend
"""

import os
import sys
import subprocess
import platform
import time
import signal
import threading
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.ENDC}")

def run_command(command, cwd=None, shell=True, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print_error(f"Error: {e.stderr}")
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print_header("CHECKING PREREQUISITES")

    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
        print_success(f"Python: {python_version}")
    except Exception as e:
        print_error(f"Python check failed: {e}")
        return False

    # Check Node.js
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print_success(f"Node.js: {node_version}")
    except Exception as e:
        print_error("Node.js not found. Please install Node.js 18+ from https://nodejs.org/")
        return False

    # Check npm
    try:
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        print_success(f"npm: {npm_version}")
    except Exception as e:
        print_error("npm not found")
        return False

    return True

def find_project_directories():
    """Find backend and frontend directories"""
    current_dir = Path.cwd()

    # Look for backend directory
    backend_candidates = [
        current_dir / "flexpesa-ai",
        current_dir / "backend",
        current_dir / "api",
        current_dir,  # Current directory might be backend
    ]

    backend_dir = None
    for candidate in backend_candidates:
        if (candidate / "requirements.txt").exists() or (candidate / "app").exists():
            backend_dir = candidate
            break

    # Look for frontend directory
    frontend_candidates = [
        current_dir / "flexpesa-client",
        current_dir / "frontend",
        current_dir / "client",
        current_dir,  # Current directory might be frontend
    ]

    frontend_dir = None
    for candidate in frontend_candidates:
        if (candidate / "package.json").exists() and (candidate / "next.config.ts").exists():
            frontend_dir = candidate
            break

    return backend_dir, frontend_dir

def setup_backend(backend_dir):
    """Set up Python virtual environment and install backend dependencies"""
    print_header("SETTING UP BACKEND")

    if not backend_dir:
        print_error("Backend directory not found")
        return False

    print_info(f"Backend directory: {backend_dir}")

    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print_info("Creating virtual environment...")
        result = run_command(f"{sys.executable} -m venv venv", cwd=backend_dir)
        if not result:
            return False
        print_success("Virtual environment created")
    else:
        print_success("Virtual environment already exists")

    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = venv_dir / "Scripts" / "activate.bat"
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        activate_script = venv_dir / "bin" / "activate"
        pip_path = venv_dir / "bin" / "pip"

    # Install requirements
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        print_info("Installing Python dependencies...")
        result = run_command(f"{pip_path} install -r requirements.txt", cwd=backend_dir)
        if not result:
            print_warning("Some packages might have failed to install, but continuing...")
        print_success("Backend dependencies installed")
    else:
        print_warning("requirements.txt not found, skipping dependency installation")

    return True

def setup_frontend(frontend_dir):
    """Set up frontend dependencies"""
    print_header("SETTING UP FRONTEND")

    if not frontend_dir:
        print_error("Frontend directory not found")
        return False

    print_info(f"Frontend directory: {frontend_dir}")

    # Install npm dependencies
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print_info("Installing Node.js dependencies...")
        result = run_command("npm install", cwd=frontend_dir)
        if not result:
            return False
        print_success("Frontend dependencies installed")
    else:
        print_success("Frontend dependencies already installed")

    return True

def check_ports():
    """Check if required ports are available"""
    import socket

    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0

    backend_port = 8000
    frontend_port = 3000

    if is_port_open(backend_port):
        print_warning(f"Port {backend_port} is already in use (backend)")
        return False

    if is_port_open(frontend_port):
        print_warning(f"Port {frontend_port} is already in use (frontend)")
        return False

    return True

def start_backend(backend_dir):
    """Start the backend server"""
    if platform.system() == "Windows":
        python_path = backend_dir / "venv" / "Scripts" / "python"
    else:
        python_path = backend_dir / "venv" / "bin" / "python"

    # Try different ways to start the backend
    run_py = backend_dir / "run.py"
    if run_py.exists():
        cmd = f"{python_path} run.py"
    else:
        cmd = f"{python_path} -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

    print_info(f"Starting backend with: {cmd}")

    return subprocess.Popen(
        cmd,
        shell=True,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

def start_frontend(frontend_dir):
    """Start the frontend server"""
    cmd = "npm run dev"
    print_info(f"Starting frontend with: {cmd}")

    return subprocess.Popen(
        cmd,
        shell=True,
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

def monitor_process(process, name, color):
    """Monitor and display output from a process"""
    def read_output():
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"{color}[{name}]{Colors.ENDC} {line.rstrip()}")

    thread = threading.Thread(target=read_output, daemon=True)
    thread.start()
    return thread

def create_env_files(backend_dir, frontend_dir):
    """Create basic .env files if they don't exist"""
    print_header("CONFIGURING ENVIRONMENT")

    # Backend .env
    if backend_dir:
        backend_env = backend_dir / ".env"
        if not backend_env.exists():
            env_content = """# Environment
ENVIRONMENT=development
DEBUG=true

# Database (update with your PostgreSQL credentials)
DATABASE_URL=postgresql://portfolio_user:portfolio_password@localhost:5432/portfolio_db

# Security
SECRET_KEY=dev-secret-key-change-in-production

# Authentication (disabled for development)
DISABLE_AUTH=true

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000

# Server
HOST=0.0.0.0
BACKEND_PORT=8000
"""
            backend_env.write_text(env_content)
            print_success("Created backend .env file")
        else:
            print_success("Backend .env file already exists")

    # Frontend .env.local
    if frontend_dir:
        frontend_env = frontend_dir / ".env.local"
        if not frontend_env.exists():
            env_content = """# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BACKEND_PORT=8000
NEXT_PUBLIC_API_TIMEOUT=15000

# Development flags
NODE_ENV=development
"""
            frontend_env.write_text(env_content)
            print_success("Created frontend .env.local file")
        else:
            print_success("Frontend .env.local file already exists")

def main():
    """Main execution function"""
    print_header("FLEXPESA PORTFOLIO - FULL STACK RUNNER")

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print(f"\n{Colors.WARNING}Shutting down servers...{Colors.ENDC}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites not met. Please install missing tools.")
        sys.exit(1)

    # Find project directories
    backend_dir, frontend_dir = find_project_directories()

    if not backend_dir:
        print_error("Backend directory not found. Please run this script from the project root.")
        sys.exit(1)

    if not frontend_dir:
        print_error("Frontend directory not found. Please run this script from the project root.")
        sys.exit(1)

    # Create environment files
    create_env_files(backend_dir, frontend_dir)

    # Setup backend
    if not setup_backend(backend_dir):
        print_error("Backend setup failed")
        sys.exit(1)

    # Setup frontend
    if not setup_frontend(frontend_dir):
        print_error("Frontend setup failed")
        sys.exit(1)

    # Check ports
    if not check_ports():
        print_error("Required ports are not available")
        sys.exit(1)

    # Start servers
    print_header("STARTING SERVERS")

    try:
        # Start backend
        backend_process = start_backend(backend_dir)
        backend_thread = monitor_process(backend_process, "BACKEND", Colors.BLUE)

        # Wait a moment for backend to start
        time.sleep(3)

        # Start frontend
        frontend_process = start_frontend(frontend_dir)
        frontend_thread = monitor_process(frontend_process, "FRONTEND", Colors.GREEN)

        # Print success message
        time.sleep(2)
        print_header("SERVERS RUNNING")
        print_success("Backend API: http://localhost:8000")
        print_success("Frontend App: http://localhost:3000")
        print_success("API Docs: http://localhost:8000/docs")
        print_info("Press Ctrl+C to stop all servers")

        # Wait for processes
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Stopping servers...{Colors.ENDC}")
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait()
            frontend_process.wait()
            print_success("All servers stopped")

    except Exception as e:
        print_error(f"Error starting servers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()