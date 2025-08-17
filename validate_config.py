#!/usr/bin/env python3
"""
Puper API Configuration Validator
=================================
This script validates your .env configuration and checks system requirements.
"""

import os
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlparse

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} not found: {filepath}")
        return False

def check_env_var(var_name: str, description: str, required: bool = True) -> bool:
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value:
        # Hide sensitive values
        if any(sensitive in var_name.lower() for sensitive in ['password', 'secret', 'key']):
            display_value = "***" if len(value) > 3 else value
        else:
            display_value = value
        print(f"✅ {description}: {display_value}")
        return True
    else:
        status = "❌" if required else "⚠️"
        req_text = "required" if required else "optional"
        print(f"{status} {description} not set ({req_text}): {var_name}")
        return not required

def check_database_url(url: str) -> bool:
    """Validate database URL format"""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['postgresql', 'postgres']:
            print(f"❌ Database URL should use postgresql:// scheme")
            return False
        if not parsed.hostname:
            print(f"❌ Database URL missing hostname")
            return False
        if not parsed.path or parsed.path == '/':
            print(f"❌ Database URL missing database name")
            return False
        print(f"✅ Database URL format is valid")
        return True
    except Exception as e:
        print(f"❌ Invalid database URL format: {e}")
        return False

def check_redis_url(url: str) -> bool:
    """Validate Redis URL format"""
    try:
        parsed = urlparse(url)
        if parsed.scheme != 'redis':
            print(f"❌ Redis URL should use redis:// scheme")
            return False
        print(f"✅ Redis URL format is valid")
        return True
    except Exception as e:
        print(f"❌ Invalid Redis URL format: {e}")
        return False

def check_python_packages():
    """Check if required Python packages are available"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'redis',
        'passlib',
        'jose',
        'pydantic'
    ]
    
    print("\n📦 Checking Python packages...")
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            all_good = False
    
    return all_good

def check_docker():
    """Check if Docker and Docker Compose are available"""
    print("\n🐳 Checking Docker...")
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
        else:
            print(f"❌ Docker not available")
            return False
    except FileNotFoundError:
        print(f"❌ Docker not installed")
        return False
    
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose: {result.stdout.strip()}")
            return True
        else:
            # Try docker compose (newer syntax)
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker Compose: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Docker Compose not available")
                return False
    except FileNotFoundError:
        print(f"❌ Docker Compose not installed")
        return False

def main():
    """Main validation function"""
    print("🚽 Puper API Configuration Validator")
    print("=" * 50)
    
    # Load .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        print("📄 Loading .env file...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    all_checks_passed = True
    
    # Check required files
    print("\n📁 Checking required files...")
    all_checks_passed &= check_file_exists('.env', '.env configuration file')
    all_checks_passed &= check_file_exists('main.py', 'Main application file')
    all_checks_passed &= check_file_exists('requirements.txt', 'Requirements file')
    
    # Check environment variables
    print("\n🔧 Checking environment variables...")
    all_checks_passed &= check_env_var('DATABASE_URL', 'Database URL', required=True)
    all_checks_passed &= check_env_var('SECRET_KEY', 'Secret key', required=True)
    all_checks_passed &= check_env_var('REDIS_URL', 'Redis URL', required=True)
    all_checks_passed &= check_env_var('ENVIRONMENT', 'Environment', required=False)
    all_checks_passed &= check_env_var('GOOGLE_MAPS_API_KEY', 'Google Maps API key', required=False)
    
    # Validate URL formats
    print("\n🔗 Validating URL formats...")
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        all_checks_passed &= check_database_url(database_url)
    
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        all_checks_passed &= check_redis_url(redis_url)
    
    # Check secret key strength
    secret_key = os.getenv('SECRET_KEY', '')
    if secret_key:
        if len(secret_key) < 32:
            print("⚠️  Secret key should be at least 32 characters long")
            all_checks_passed = False
        elif secret_key in ['your-super-secret-key-change-this-in-production', 'dev-secret-key-change-in-production']:
            print("⚠️  Using default secret key - change this for production!")
            if os.getenv('ENVIRONMENT') == 'production':
                all_checks_passed = False
    
    # Check Python packages
    all_checks_passed &= check_python_packages()
    
    # Check Docker (optional)
    docker_available = check_docker()
    
    # Final summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 All configuration checks passed!")
        print("\n🚀 You can start the API with:")
        if docker_available:
            print("   ./start.sh")
            print("   or")
            print("   docker-compose up -d")
        print("   python main.py")
        print("   or")
        print("   uvicorn main:app --reload")
    else:
        print("❌ Some configuration issues found. Please fix them before starting the API.")
        print("\n💡 Common fixes:")
        print("   - Copy .env.example to .env and update values")
        print("   - Install requirements: pip install -r requirements.txt")
        print("   - Set up PostgreSQL with PostGIS extension")
        print("   - Set up Redis server")
        print("   - Generate a strong SECRET_KEY")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
