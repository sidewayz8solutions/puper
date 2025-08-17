#!/usr/bin/env python3
"""
Puper API Database Migration Helper
==================================
This script provides easy commands for managing database migrations with Alembic.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd: list, description: str):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def check_alembic():
    """Check if Alembic is installed"""
    try:
        subprocess.run(['alembic', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Alembic not found. Install it with: pip install alembic")
        return False

def init_migrations():
    """Initialize the migration environment"""
    if Path('alembic').exists():
        print("⚠️  Alembic directory already exists. Skipping initialization.")
        return True
    
    return run_command(['alembic', 'init', 'alembic'], "Initializing Alembic")

def create_migration(message: str = None):
    """Create a new migration"""
    if not message:
        message = input("Enter migration message: ").strip()
        if not message:
            message = "Auto-generated migration"
    
    cmd = ['alembic', 'revision', '--autogenerate', '-m', message]
    return run_command(cmd, f"Creating migration: {message}")

def upgrade_database(revision: str = "head"):
    """Upgrade database to a specific revision"""
    cmd = ['alembic', 'upgrade', revision]
    return run_command(cmd, f"Upgrading database to {revision}")

def downgrade_database(revision: str):
    """Downgrade database to a specific revision"""
    cmd = ['alembic', 'downgrade', revision]
    return run_command(cmd, f"Downgrading database to {revision}")

def show_history():
    """Show migration history"""
    cmd = ['alembic', 'history', '--verbose']
    return run_command(cmd, "Showing migration history")

def show_current():
    """Show current revision"""
    cmd = ['alembic', 'current']
    return run_command(cmd, "Showing current revision")

def show_heads():
    """Show head revisions"""
    cmd = ['alembic', 'heads']
    return run_command(cmd, "Showing head revisions")

def stamp_database(revision: str = "head"):
    """Stamp database with a specific revision without running migrations"""
    cmd = ['alembic', 'stamp', revision]
    return run_command(cmd, f"Stamping database with {revision}")

def show_help():
    """Show help message"""
    print("""
🚽 Puper API Migration Helper

Usage: python migrate.py <command> [options]

Commands:
  init                    Initialize Alembic (first time setup)
  create [message]        Create a new migration
  upgrade [revision]      Upgrade database (default: head)
  downgrade <revision>    Downgrade database to revision
  history                 Show migration history
  current                 Show current database revision
  heads                   Show head revisions
  stamp [revision]        Stamp database with revision (default: head)
  help                    Show this help message

Examples:
  python migrate.py init
  python migrate.py create "Add user table"
  python migrate.py upgrade
  python migrate.py downgrade -1
  python migrate.py history
  python migrate.py current

Environment Variables:
  DATABASE_URL           PostgreSQL connection string
  
Note: Make sure your .env file is configured with the correct DATABASE_URL
""")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return 1
    
    # Load environment variables from .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # Check if Alembic is available
    if not check_alembic():
        return 1
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        show_help()
    elif command == 'init':
        init_migrations()
    elif command == 'create':
        message = sys.argv[2] if len(sys.argv) > 2 else None
        create_migration(message)
    elif command == 'upgrade':
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade_database(revision)
    elif command == 'downgrade':
        if len(sys.argv) < 3:
            print("❌ Downgrade requires a revision argument")
            return 1
        downgrade_database(sys.argv[2])
    elif command == 'history':
        show_history()
    elif command == 'current':
        show_current()
    elif command == 'heads':
        show_heads()
    elif command == 'stamp':
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        stamp_database(revision)
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
