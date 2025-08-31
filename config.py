#!/usr/bin/env python3
"""
Configuration Manager for Investment Portfolio MVP
Easily switch between different environment configurations
"""

import os
import shutil
import sys
from pathlib import Path
import argparse

class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    END = '\033[0m'

class ConfigManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.env_file = self.root_dir / ".env"
        self.backend_env = self.root_dir / "flexpesa-ai" / ".env"
        self.frontend_env = self.root_dir / "flexpesa-client" / ".env.local"

        print(f"🔧 Working directory: {self.root_dir}")
        print(f"📄 Root .env file: {self.env_file}")
        print(f"🔙 Backend .env file: {self.backend_env}")
        print(f"🎨 Frontend .env file: {self.frontend_env}")

        # Predefined configurations
        self.configs = {
            'native': {
                'description': 'Native development (Backend: 8000, Docker: 8080)',
                'env': {
                    'BACKEND_PORT': '8000',
                    'DOCKER_BACKEND_PORT': '8080',
                    'FRONTEND_PORT': '3000',
                    'NEXT_PUBLIC_API_URL': 'http://localhost:8000/api/v1',
                    'DOCKER_ENV': 'false',
                    'ENVIRONMENT': 'development',
                    'DEBUG': 'true',
                }
            },
            'docker': {
                'description': 'Docker development (Backend Docker: 8080)',
                'env': {
                    'BACKEND_PORT': '8001',  # Avoid conflict with Docker
                    'DOCKER_BACKEND_PORT': '8080',
                    'FRONTEND_PORT': '3000',
                    'NEXT_PUBLIC_API_URL': 'http://localhost:8080/api/v1',
                    'DOCKER_ENV': 'true',
                    'ENVIRONMENT': 'development',
                    'DEBUG': 'true',
                }
            },
            'production': {
                'description': 'Production deployment',
                'env': {
                    'BACKEND_PORT': '8000',
                    'DOCKER_BACKEND_PORT': '8080',
                    'FRONTEND_PORT': '3000',
                    'NEXT_PUBLIC_API_URL': 'https://api.yourdomain.com/api/v1',
                    'DOCKER_ENV': 'false',
                    'ENVIRONMENT': 'production',
                    'DEBUG': 'false',
                }
            },
            'custom-ports': {
                'description': 'Custom ports (Backend: 9000, Docker: 9080)',
                'env': {
                    'BACKEND_PORT': '9000',
                    'DOCKER_BACKEND_PORT': '9080',
                    'FRONTEND_PORT': '3000',
                    'NEXT_PUBLIC_API_URL': 'http://localhost:9000/api/v1',
                    'DOCKER_ENV': 'false',
                    'ENVIRONMENT': 'development',
                    'DEBUG': 'true',
                }
            }
        }

    def print_current_config(self):
        """Display current configuration"""
        if not self.env_file.exists():
            print(f"{Colors.YELLOW}No .env file found{Colors.END}")
            return

        print(f"{Colors.BLUE}Current Configuration (.env):{Colors.END}")
        print("-" * 40)

        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if any(port_key in key.upper() for port_key in ['PORT', 'URL']):
                        print(f"{Colors.GREEN}{key}{Colors.END} = {value}")

    def list_configs(self):
        """List available configurations"""
        print(f"{Colors.BLUE}Available Configurations:{Colors.END}")
        print("-" * 50)

        for name, config in self.configs.items():
            print(f"\n{Colors.GREEN}{name}{Colors.END}")
            print(f"  Description: {config['description']}")
            print(f"  Backend Port: {config['env']['BACKEND_PORT']}")
            print(f"  Docker Port: {config['env']['DOCKER_BACKEND_PORT']}")
            print(f"  API URL: {config['env']['NEXT_PUBLIC_API_URL']}")

    def apply_config(self, config_name):
        """Apply a specific configuration"""
        if config_name not in self.configs:
            print(f"{Colors.RED}Error: Configuration '{config_name}' not found{Colors.END}")
            self.list_configs()
            return False

        config = self.configs[config_name]

        # Backup existing .env if it exists
        if self.env_file.exists():
            backup_file = self.env_file.with_suffix('.env.backup')
            shutil.copy2(self.env_file, backup_file)
            print(f"{Colors.YELLOW}Backed up existing .env to {backup_file}{Colors.END}")

        # Write new root .env configuration
        self.write_root_env(config_name, config)

        # Write backend-specific .env
        self.write_backend_env(config)

        # Write frontend .env.local
        self.write_frontend_env(config['env'])

        print(f"{Colors.GREEN}✅ Applied configuration: {config_name}{Colors.END}")
        print(f"Description: {config['description']}")

        return True

    def write_root_env(self, config_name, config):
        """Write root .env file"""
        env_content = f"""# Investment Portfolio MVP - Environment Configuration
# Generated by config.py - Configuration: {config_name}
# {config['description']}

# =================================================================
# PORT CONFIGURATION
# =================================================================

"""

        # Add all environment variables
        for key, value in config['env'].items():
            env_content += f"{key}={value}\n"

        # Add common configuration with environment-specific database URL
        if config['env']['DOCKER_ENV'] == 'true':
            # Full Docker environment - use service hostnames
            db_url = "postgresql://portfolio_user:portfolio_password@postgres:5432/portfolio_db"
        else:
            # Native backend with Docker PostgreSQL - use localhost
            db_url = "postgresql://portfolio_user:portfolio_password@localhost:5432/portfolio_db"

        env_content += f"""
# =================================================================
# DATABASE CONFIGURATION
# =================================================================

DATABASE_URL={db_url}
POSTGRES_DB=portfolio_db
POSTGRES_USER=portfolio_user
POSTGRES_PASSWORD=portfolio_password
POSTGRES_PORT=5432
REDIS_PORT=6379

# =================================================================
# SECURITY (Change in production!)
# =================================================================

SECRET_KEY=your-secret-key-change-in-production-abc123def456ghi789jkl
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# =================================================================
# OPTIONAL API KEYS
# =================================================================

NEWS_API_KEY=your_news_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# =================================================================
# CORS CONFIGURATION
# =================================================================

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://frontend:3000
"""

        with open(self.env_file, 'w') as f:
            f.write(env_content)

    def write_backend_env(self, config):
        """Write backend .env file"""
        # Determine database URL based on environment
        if config['env']['DOCKER_ENV'] == 'true':
            # Docker environment - use 'postgres' hostname
            db_url = "postgresql://portfolio_user:portfolio_password@postgres:5432/portfolio_db"
        else:
            # Native environment - use localhost
            db_url = "postgresql://portfolio_user:portfolio_password@localhost:5432/portfolio_db"

        backend_content = f"""# Backend Environment Configuration
# Auto-generated by config.py

# Port Configuration
BACKEND_PORT={config['env']['BACKEND_PORT']}
PORT={config['env']['BACKEND_PORT']}
HOST=0.0.0.0

# Environment
ENVIRONMENT={config['env']['ENVIRONMENT']}
DEBUG={config['env']['DEBUG']}

# Database (configured for {'Docker' if config['env']['DOCKER_ENV'] == 'true' else 'Native'} environment)
DATABASE_URL={db_url}

# Security
SECRET_KEY=your-secret-key-change-in-production-abc123def456ghi789jkl

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://frontend:3000

# API Keys (optional)
NEWS_API_KEY=your_news_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
"""

        # Create backend directory if it doesn't exist
        self.backend_env.parent.mkdir(exist_ok=True)

        with open(self.backend_env, 'w') as f:
            f.write(backend_content)

        print(f"{Colors.GREEN}✅ Updated backend .env file{Colors.END}")

    def write_frontend_env(self, env_vars):
        """Write frontend .env.local file"""
        content = f"""# Generated by config.py
NEXT_PUBLIC_API_URL={env_vars['NEXT_PUBLIC_API_URL']}
NEXT_PUBLIC_BACKEND_PORT={env_vars['BACKEND_PORT']}
NEXT_PUBLIC_DOCKER_BACKEND_PORT={env_vars['DOCKER_BACKEND_PORT']}
NEXT_PUBLIC_DOCKER_ENV={env_vars['DOCKER_ENV']}
NODE_ENV={env_vars['ENVIRONMENT']}
"""

        # Create frontend directory if it doesn't exist
        self.frontend_env.parent.mkdir(exist_ok=True)

        with open(self.frontend_env, 'w') as f:
            f.write(content)

        print(f"{Colors.GREEN}✅ Updated frontend .env.local file{Colors.END}")

def main():
    parser = argparse.ArgumentParser(description='Manage Investment Portfolio configurations')
    parser.add_argument('action', choices=['list', 'show', 'set'],
                       help='Action to perform')
    parser.add_argument('config', nargs='?',
                       help='Configuration name to set')

    args = parser.parse_args()

    manager = ConfigManager()

    if args.action == 'list':
        manager.list_configs()
    elif args.action == 'show':
        manager.print_current_config()
    elif args.action == 'set':
        if not args.config:
            print(f"{Colors.RED}Error: Configuration name required{Colors.END}")
            manager.list_configs()
            sys.exit(1)
        manager.apply_config(args.config)

if __name__ == "__main__":
    main()