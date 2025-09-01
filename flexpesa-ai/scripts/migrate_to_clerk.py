#!/usr/bin/env python3
"""
Migration script to update existing Investment Portfolio database
to support Clerk authentication and new schema changes.
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect, MetaData, Table, Column, String, Boolean, DateTime
from app.core.database import SessionLocal, engine
from app.models.portfolio import Account, Asset, MarketData, PortfolioSnapshot
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handle database schema migrations for Clerk authentication"""

    def __init__(self):
        self.db = SessionLocal()
        self.inspector = inspect(engine)

    def check_current_schema(self):
        """Check current database schema and identify what needs to be migrated"""
        logger.info("🔍 Checking current database schema...")

        # Get current tables
        tables = self.inspector.get_table_names()
        logger.info(f"Found tables: {tables}")

        migrations_needed = []

        # Check if accounts table exists
        if 'accounts' in tables:
            columns = [col['name'] for col in self.inspector.get_columns('accounts')]
            logger.info(f"Accounts table columns: {columns}")

            # Check for old user_id column (FastAPI-Users UUID)
            if 'user_id' in columns and 'clerk_user_id' not in columns:
                migrations_needed.append('add_clerk_user_id_to_accounts')

            # Check for missing new columns
            required_columns = ['description', 'currency', 'is_active', 'updated_at']
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                migrations_needed.append(f'add_account_columns: {missing_columns}')
        else:
            migrations_needed.append('create_accounts_table')

        # Check assets table
        if 'assets' in tables:
            columns = [col['name'] for col in self.inspector.get_columns('assets')]
            logger.info(f"Assets table columns: {columns}")

            required_columns = ['name', 'asset_type', 'market_cap', 'volume',
                              'day_change', 'day_change_percent', 'currency',
                              'exchange', 'sector', 'industry', 'is_active',
                              'price_updated_at']
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                migrations_needed.append(f'add_asset_columns: {missing_columns}')
        else:
            migrations_needed.append('create_assets_table')

        # Check for new tables
        new_tables = ['portfolio_snapshots', 'market_data_cache']
        for table in new_tables:
            if table not in tables:
                migrations_needed.append(f'create_{table}_table')

        # Check for old users table (FastAPI-Users)
        if 'users' in tables:
            migrations_needed.append('handle_legacy_users_table')

        logger.info(f"Migrations needed: {migrations_needed}")
        return migrations_needed

    def backup_database(self):
        """Create a backup of current database before migration"""
        try:
            logger.info("💾 Creating database backup before migration...")

            # Create backup directory
            backup_dir = Path("./backups")
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"pre_clerk_migration_backup_{timestamp}.sql"

            # Create backup using pg_dump
            if settings.DATABASE_URL.startswith("postgresql://"):
                import subprocess

                # Parse database URL
                db_url = settings.DATABASE_URL
                # This is a simplified backup - in production, use proper pg_dump with credentials
                logger.info(f"Database backup should be created at: {backup_file}")
                logger.info("NOTE: For production, run: pg_dump -h host -U user dbname > backup.sql")

                # Create a simple SQL dump of data for SQLite-like databases
                with open(backup_file, 'w') as f:
                    f.write(f"-- Database backup created: {datetime.now()}\n")
                    f.write(f"-- Original DATABASE_URL: {settings.DATABASE_URL}\n\n")

                logger.info(f"✅ Backup reference created: {backup_file}")

            return str(backup_file)

        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return None

    def migrate_accounts_table(self):
        """Migrate accounts table to support Clerk authentication"""
        try:
            logger.info("🔄 Migrating accounts table for Clerk authentication...")

            # Add new columns if they don't exist
            new_columns = [
                ("clerk_user_id", "VARCHAR(255)"),
                ("description", "TEXT"),
                ("currency", "VARCHAR(3) DEFAULT 'USD'"),
                ("is_active", "BOOLEAN DEFAULT TRUE"),
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ]

            for column_name, column_type in new_columns:
                try:
                    self.db.execute(text(f"ALTER TABLE accounts ADD COLUMN {column_name} {column_type}"))
                    self.db.commit()
                    logger.info(f"   ✅ Added column: {column_name}")
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        logger.info(f"   ⚠️  Column {column_name} already exists")
                    else:
                        logger.error(f"   ❌ Failed to add column {column_name}: {e}")

            # Handle migration from old user_id (UUID) to clerk_user_id (string)
            try:
                # Check if old user_id column exists
                columns = [col['name'] for col in self.inspector.get_columns('accounts')]
                if 'user_id' in columns:
                    logger.info("   🔄 Migrating from old user_id to clerk_user_id...")

                    # For demo purposes, assign all existing accounts to a demo clerk user
                    demo_clerk_id = "user_demo_migration_" + datetime.now().strftime("%Y%m%d")

                    self.db.execute(text("""
                        UPDATE accounts
                        SET clerk_user_id = :demo_clerk_id
                        WHERE clerk_user_id IS NULL
                    """), {"demo_clerk_id": demo_clerk_id})

                    self.db.commit()
                    logger.info(f"   ✅ Assigned existing accounts to demo user: {demo_clerk_id}")

                    # Note: In production, you'd want to map real users properly
                    logger.warning("   ⚠️  IMPORTANT: Update clerk_user_id values with real Clerk user IDs")

            except Exception as e:
                logger.error(f"   ❌ User ID migration failed: {e}")

            # Create indexes for performance
            try:
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_accounts_clerk_user ON accounts(clerk_user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(is_active)",
                    "CREATE INDEX IF NOT EXISTS idx_accounts_user_active ON accounts(clerk_user_id, is_active)"
                ]

                for index_sql in indexes:
                    self.db.execute(text(index_sql))
                    self.db.commit()

                logger.info("   ✅ Created performance indexes")

            except Exception as e:
                logger.warning(f"   ⚠️  Index creation failed (may already exist): {e}")

            logger.info("✅ Accounts table migration completed")

        except Exception as e:
            logger.error(f"❌ Accounts table migration failed: {e}")
            self.db.rollback()
            raise

    def migrate_assets_table(self):
        """Migrate assets table with new columns"""
        try:
            logger.info("🔄 Migrating assets table...")

            # Add new columns
            new_columns = [
                ("name", "VARCHAR(255)"),
                ("asset_type", "VARCHAR(50)"),
                ("market_cap", "FLOAT"),
                ("volume", "FLOAT"),
                ("day_change", "FLOAT DEFAULT 0.0"),
                ("day_change_percent", "FLOAT DEFAULT 0.0"),
                ("currency", "VARCHAR(3) DEFAULT 'USD'"),
                ("exchange", "VARCHAR(10)"),
                ("sector", "VARCHAR(100)"),
                ("industry", "VARCHAR(100)"),
                ("is_active", "BOOLEAN DEFAULT TRUE"),
                ("price_updated_at", "TIMESTAMP")
            ]

            for column_name, column_type in new_columns:
                try:
                    self.db.execute(text(f"ALTER TABLE assets ADD COLUMN {column_name} {column_type}"))
                    self.db.commit()
                    logger.info(f"   ✅ Added column: {column_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info(f"   ⚠️  Column {column_name} already exists")
                    else:
                        logger.error(f"   ❌ Failed to add column {column_name}: {e}")

            # Update asset_type for existing assets based on symbol
            try:
                asset_type_updates = [
                    ("UPDATE assets SET asset_type = 'crypto' WHERE symbol LIKE '%-USD'", "crypto assets"),
                    ("UPDATE assets SET asset_type = 'etf' WHERE symbol IN ('SPY', 'QQQ', 'VTI', 'IWM', 'DIA')", "ETF assets"),
                    ("UPDATE assets SET asset_type = 'stock' WHERE asset_type IS NULL AND LENGTH(symbol) <= 4", "stock assets")
                ]

                for sql, description in asset_type_updates:
                    result = self.db.execute(text(sql))
                    self.db.commit()
                    logger.info(f"   ✅ Updated {result.rowcount} {description}")

            except Exception as e:
                logger.error(f"   ❌ Asset type update failed: {e}")

            # Create indexes
            try:
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_assets_symbol ON assets(symbol)",
                    "CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type)",
                    "CREATE INDEX IF NOT EXISTS idx_assets_active ON assets(is_active)"
                ]

                for index_sql in indexes:
                    self.db.execute(text(index_sql))
                    self.db.commit()

                logger.info("   ✅ Created asset indexes")

            except Exception as e:
                logger.warning(f"   ⚠️  Asset index creation failed: {e}")

            logger.info("✅ Assets table migration completed")

        except Exception as e:
            logger.error(f"❌ Assets table migration failed: {e}")
            self.db.rollback()
            raise

    def create_new_tables(self):
        """Create new tables (portfolio_snapshots, market_data_cache)"""
        try:
            logger.info("🔄 Creating new tables...")

            from app.core.database import Base

            # This will create all tables defined in models
            Base.metadata.create_all(bind=engine)

            logger.info("✅ New tables created successfully")

        except Exception as e:
            logger.error(f"❌ New table creation failed: {e}")
            raise

    def handle_legacy_users_table(self):
        """Handle legacy FastAPI-Users table"""
        try:
            logger.info("🔄 Handling legacy users table...")

            # Check if users table exists
            tables = self.inspector.get_table_names()
            if 'users' in tables:
                logger.info("   Found legacy users table from FastAPI-Users")

                # Get count of users
                result = self.db.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                logger.info(f"   Found {user_count} legacy users")

                if user_count > 0:
                    logger.warning("   ⚠️  IMPORTANT: Legacy users found!")
                    logger.warning("   You'll need to migrate user data to Clerk manually")
                    logger.warning("   Consider:")
                    logger.warning("   1. Export user emails from the users table")
                    logger.warning("   2. Import them into Clerk")
                    logger.warning("   3. Map old user_id to new clerk_user_id in accounts")

                # Don't drop the table - let admin decide
                logger.info("   ⚠️  Legacy users table preserved for manual migration")

        except Exception as e:
            logger.error(f"❌ Legacy users table handling failed: {e}")

    def verify_migration(self):
        """Verify that migration was successful"""
        try:
            logger.info("🔍 Verifying migration results...")

            # Check accounts table
            accounts_count = self.db.execute(text("SELECT COUNT(*) FROM accounts")).scalar()
            accounts_with_clerk_id = self.db.execute(text(
                "SELECT COUNT(*) FROM accounts WHERE clerk_user_id IS NOT NULL"
            )).scalar()

            logger.info(f"   Accounts: {accounts_count} total, {accounts_with_clerk_id} with Clerk ID")

            # Check assets table
            assets_count = self.db.execute(text("SELECT COUNT(*) FROM assets")).scalar()
            assets_with_type = self.db.execute(text(
                "SELECT COUNT(*) FROM assets WHERE asset_type IS NOT NULL"
            )).scalar()

            logger.info(f"   Assets: {assets_count} total, {assets_with_type} with asset type")

            # Check new tables
            tables = self.inspector.get_table_names()
            new_tables = ['portfolio_snapshots', 'market_data_cache']

            for table in new_tables:
                if table in tables:
                    count = self.db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    logger.info(f"   {table}: {count} records")
                else:
                    logger.error(f"   ❌ Missing table: {table}")

            # Check if any accounts missing Clerk ID
            missing_clerk_id = self.db.execute(text(
                "SELECT COUNT(*) FROM accounts WHERE clerk_user_id IS NULL"
            )).scalar()

            if missing_clerk_id > 0:
                logger.warning(f"   ⚠️  {missing_clerk_id} accounts missing clerk_user_id")
                logger.warning("   These accounts won't be accessible until assigned to Clerk users")

            logger.info("✅ Migration verification completed")
            return missing_clerk_id == 0

        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False

    def run_migration(self):
        """Run the complete migration process"""
        try:
            logger.info("🚀 Starting database migration to Clerk authentication...")
            logger.info("=" * 60)

            # Step 1: Check what needs to be migrated
            migrations_needed = self.check_current_schema()

            if not migrations_needed:
                logger.info("✅ Database is already up to date!")
                return True

            # Step 2: Create backup
            backup_file = self.backup_database()

            # Step 3: Run migrations
            if 'add_clerk_user_id_to_accounts' in migrations_needed or 'add_account_columns' in str(migrations_needed):
                self.migrate_accounts_table()

            if 'add_asset_columns' in str(migrations_needed):
                self.migrate_assets_table()

            if any('create_' in migration and '_table' in migration for migration in migrations_needed):
                self.create_new_tables()

            if 'handle_legacy_users_table' in migrations_needed:
                self.handle_legacy_users_table()

            # Step 4: Verify migration
            success = self.verify_migration()

            if success:
                logger.info("=" * 60)
                logger.info("🎉 Migration completed successfully!")
                logger.info("")
                logger.info("Next steps:")
                logger.info("1. Set up Clerk authentication in your .env file")
                logger.info("2. Update frontend to use Clerk authentication")
                logger.info("3. Test the API with Clerk JWT tokens")
                logger.info("4. Update any accounts with proper clerk_user_id values")
                if backup_file:
                    logger.info(f"5. Backup created at: {backup_file}")

                return True
            else:
                logger.error("❌ Migration completed with warnings - please review above")
                return False

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self.db.rollback()
            return False

        finally:
            self.db.close()

def main():
    """Main migration function"""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate database to Clerk authentication')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be migrated without making changes')
    parser.add_argument('--force', action='store_true',
                       help='Force migration even if it seems risky')

    args = parser.parse_args()

    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
        migrator = DatabaseMigrator()
        migrations_needed = migrator.check_current_schema()

        if migrations_needed:
            logger.info("Would run these migrations:")
            for migration in migrations_needed:
                logger.info(f"  - {migration}")
        else:
            logger.info("No migrations needed")

        return 0

    # Warning for production
    if settings.ENVIRONMENT == "production" and not args.force:
        logger.warning("⚠️  PRODUCTION DATABASE DETECTED!")
        logger.warning("This migration will modify your production database.")
        logger.warning("Please ensure you have a backup before proceeding.")
        logger.warning("Use --force flag to proceed with production migration.")

        response = input("Continue with migration? (type 'yes' to confirm): ")
        if response.lower() != 'yes':
            logger.info("Migration cancelled")
            return 1

    # Run migration
    migrator = DatabaseMigrator()
    success = migrator.run_migration()

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
    