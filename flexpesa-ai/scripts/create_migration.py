#!/usr/bin/env python3
"""Create database migration for authentication setup"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic.config import Config
from alembic import command
from app.core.config import settings

def create_migration():
    """Create Alembic migration for User model and Account updates"""

    print("🔧 Creating authentication migration...")

    # Create alembic directory if it doesn't exist
    alembic_dir = Path(__file__).parent.parent / "alembic"
    alembic_dir.mkdir(exist_ok=True)

    # Create alembic.ini if it doesn't exist
    alembic_ini = Path(__file__).parent.parent / "alembic.ini"
    if not alembic_ini.exists():
        print("📝 Creating alembic.ini...")
        alembic_content = f"""# Alembic Config
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = {settings.DATABASE_URL}

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        with open(alembic_ini, 'w') as f:
            f.write(alembic_content)

    # Initialize Alembic if needed
    if not (alembic_dir / "env.py").exists():
        print("🔧 Initializing Alembic...")
        alembic_cfg = Config(str(alembic_ini))
        command.init(alembic_cfg, str(alembic_dir))

        # Update env.py to use our models
        env_py = alembic_dir / "env.py"
        env_content = """from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your models here
from app.core.database import Base
from app.models.user import User
from app.models.portfolio import Account, Asset

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""
        with open(env_py, 'w') as f:
            f.write(env_content)

    # Create the migration
    print("📝 Creating authentication migration...")
    alembic_cfg = Config(str(alembic_ini))
    command.revision(
        alembic_cfg,
        message="Add User model and update Account for authentication",
        autogenerate=True
    )

    print("✅ Migration created successfully!")
    print("📁 Check the alembic/versions/ directory for the new migration file")

if __name__ == "__main__":
    try:
        create_migration()
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        sys.exit(1)
        