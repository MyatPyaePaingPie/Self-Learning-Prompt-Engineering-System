#!/usr/bin/env python3
"""
Simple database migration runner for the authentication system

Usage:
    python run_migrations.py

Make sure your database connection is configured in packages/db/session.py
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from packages.db.session import get_session
import sqlalchemy as sa

def run_migration(migration_file: Path):
    """Run a single migration file"""
    print(f"Running migration: {migration_file.name}")
    
    with get_session() as session:
        # Read the migration file
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Split on semicolon and execute each statement
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement.strip().startswith('--'):
                continue  # Skip comments
            try:
                session.execute(sa.text(statement))
                print(f"  ✅ Executed: {statement[:50]}...")
            except Exception as e:
                print(f"  ❌ Error executing: {statement[:50]}...")
                print(f"     Error: {e}")
                session.rollback()
                raise
        
        session.commit()
        print(f"✅ Migration {migration_file.name} completed successfully")

def main():
    """Run all pending migrations"""
    migrations_dir = Path("packages/db/migrations")
    
    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        return
    
    # Get all .sql files and sort them
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("ℹ️  No migration files found")
        return
    
    print(f"Found {len(migration_files)} migration files")
    print("⚠️  WARNING: This will modify your database. Make sure you have backups!")
    
    # Ask for confirmation
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Run each migration
    for migration_file in migration_files:
        try:
            run_migration(migration_file)
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("💡 Fix the error and run again")
            return
    
    print("\n🎉 All migrations completed successfully!")
    print("Your database now has:")
    print("  - users table with secure password storage")
    print("  - Updated prompts table with user foreign key")
    print("  - All necessary indexes for performance")

if __name__ == "__main__":
    main()