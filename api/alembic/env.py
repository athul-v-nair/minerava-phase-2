import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

# Ensure api/ is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# No models yet for Slice 0 — target_metadata stays None
target_metadata = None

# Allow DATABASE_URL env to override alembic.ini
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
else:
    # resolve relative sqlite path to absolute for alembic
    raw = config.get_main_option("sqlalchemy.url")
    if raw and raw.startswith("sqlite:///"):
        p = raw.replace("sqlite:///", "", 1)
        if p.startswith("./") or p.startswith("../"):
            # alembic.ini is at api/alembic.ini
            base = Path(config.config_file_name).parent if config.config_file_name else Path.cwd()
            abs_path = (base / p).resolve()
            config.set_main_option("sqlalchemy.url", f"sqlite:///{abs_path}")


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
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)

    # Ensure WAL + FKs for SQLite after connection
    with connectable.connect() as connection:
        if url.startswith("sqlite"):
            connection.exec_driver_sql("PRAGMA journal_mode=WAL;")
            connection.exec_driver_sql("PRAGMA foreign_keys=ON;")
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
