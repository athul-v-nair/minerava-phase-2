import os
import sqlite3
from pathlib import Path

from alembic.config import Config

from alembic import command

# DATABASE_URL supports sqlite only for Phase-1
# e.g. sqlite:///./data/minerva.db
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / ".." / "data" / "minerva.db"
DEFAULT_DB_PATH = DEFAULT_DB_PATH.resolve()

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")


def _db_path_from_url(url: str) -> Path | None:
    if url.startswith("sqlite:///"):
        raw = url.replace("sqlite:///", "", 1)
        # handle relative ./data/... or absolute
        if raw.startswith("./"):
            return (Path(__file__).resolve().parents[2] / raw[2:]).resolve()
        p = Path(raw)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        return p
    return None


def _ensure_sqlite_pragmas(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # create file if not exists
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.commit()
    finally:
        conn.close()


def init_db():
    db_path = _db_path_from_url(DATABASE_URL)
    if db_path is not None:
        _ensure_sqlite_pragmas(db_path)

    # Run alembic upgrade head (api/alembic.ini is sibling to this file's parent)
    alembic_ini = Path(__file__).resolve().parents[1].parent / "alembic.ini"
    if alembic_ini.exists():
        cfg = Config(str(alembic_ini))
        # alembic expects script_location relative to ini dir; ensure correct
        command.upgrade(cfg, "head")
    else:
        # fallback: ensure at least WAL/FKs without alembic
        pass
