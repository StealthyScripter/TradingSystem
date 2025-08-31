import uvicorn
import os
from pathlib import Path

def get_port():
    """Get port from environment variables with fallback"""
    # Try different environment variable names
    port_sources = [
        os.getenv("PORT"),                    # Generic port (used by many hosting services)
        os.getenv("BACKEND_PORT"),            # Our custom backend port
        os.getenv("BACKEND_CONTAINER_PORT"),  # Container port
        "8000"                                # Default fallback
    ]

    for port in port_sources:
        if port:
            try:
                return int(port)
            except ValueError:
                continue

    return 8000

def load_env_file():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv

        # Look for .env files in order of preference
        env_files = [
            Path(__file__).parent / ".env",           # Local backend .env
            Path(__file__).parent.parent / ".env",    # Root project .env
        ]

        for env_file in env_files:
            if env_file.exists():
                load_dotenv(env_file)
                print(f"📄 Loaded environment from: {env_file}")
                break
        else:
            print("⚠️  No .env file found, using system environment variables")

    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables only")

if __name__ == "__main__":
    # Load environment variables
    load_env_file()

    # Get port from environment
    port = get_port()
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🚀 Starting FastAPI server on {host}:{port}")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🔧 Debug mode: {os.getenv('DEBUG', 'true')}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv('DEBUG', 'true').lower() == 'true',
        log_level=os.getenv('LOG_LEVEL', 'info').lower()
    )
    