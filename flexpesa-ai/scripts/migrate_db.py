#!/usr/bin/env python3
"""Run database migrations"""

import sys
import os
from pathlib import Path
import uuid

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic.config import Config
from alembic import command
from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.core.config import settings

def run_migration():
    """Run Alembic migrations"""
    print("🚀 Running database migrations...")

    alembic_ini = Path(__file__).parent.parent / "alembic.ini"

    if not alembic_ini.exists():
        print("❌ Alembic not initialized. Run create_migration.py first.")
        return False

    try:
        alembic_cfg = Config(str(alembic_ini))
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_default_user():
    """Create default user for existing accounts"""
    print("👤 Creating default user...")

    db = SessionLocal()
    try:
        # Check if default user already exists
        result = db.execute(text("""
            SELECT id FROM users WHERE email = 'admin@portfolio.com'
        """))
        existing_user = result.fetchone()

        if existing_user:
            print("✅ Default user already exists")
            return existing_user[0]

        # Create default user
        default_user_id = str(uuid.uuid4())

        db.execute(text("""
            INSERT INTO users (id, email, hashed_password, first_name, last_name, is_active, is_superuser, is_verified, created_at)
            VALUES (:id, :email, :password, :first_name, :last_name, :is_active, :is_superuser, :is_verified, NOW())
        """), {
            "id": default_user_id,
            "email": "admin@portfolio.com",
            "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLVBKFX1WJcj3M2", # "password"
            "first_name": "Portfolio",
            "last_name": "Admin",
            "is_active": True,
            "is_superuser": True,
            "is_verified": True
        })

        db.commit()
        print("✅ Default user created: admin@portfolio.com (password: password)")
        return default_user_id

    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def migrate_existing_accounts(default_user_id):
    """Assign existing accounts to default user"""
    print("🔄 Migrating existing accounts...")

    db = SessionLocal()
    try:
        result = db.execute(text("""
            UPDATE accounts
            SET user_id = :user_id
            WHERE user_id IS NULL
        """), {"user_id": default_user_id})

        affected_rows = result.rowcount
        db.commit()

        print(f"✅ Migrated {affected_rows} accounts to default user")

    except Exception as e:
        print(f"❌ Error migrating accounts: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main migration function"""
    print("🔧 Starting Database Migration Process")
    print("=" * 50)

    # Run migrations
    if run_migration():
        # Create default user and migrate accounts
        default_user_id = create_default_user()
        migrate_existing_accounts(default_user_id)

        print("=" * 50)
        print("🎉 Database migration completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Test with: python scripts/test_auth.py")
        print("2. Login credentials: admin@portfolio.com / password")
        return 0
    else:
        print("❌ Migration failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
    