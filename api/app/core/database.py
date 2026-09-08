import os
import sqlite3
from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from alembic import command

# DATABASE_URL supports sqlite only for Phase-1
# e.g. sqlite:///./data/minerva.db
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / ".." / "data" / "minerva.db"
DEFAULT_DB_PATH = DEFAULT_DB_PATH.resolve()

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# SQLAlchemy engine / Session (reused across requests)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):  # type: ignore[no-untyped-def]
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
    except Exception:
        pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():  # type: ignore[no-untyped-def]
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
        try:
            cfg = Config(str(alembic_ini))
            command.upgrade(cfg, "head")
        except Exception:
            pass
    # Fallback: ensure tables exist via SQLAlchemy metadata (covers Windows path bug)
    try:
        import app.models.organization  # noqa: F401
        import app.models.user  # noqa: F401
        from app.models.base import Base  # noqa: WPS433

        Base.metadata.create_all(bind=engine)
        # ensure alembic_version stamped to head so future upgrades work
        try:
            with engine.begin() as conn:
                cur = conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
                if cur.fetchone():
                    cur2 = conn.exec_driver_sql("SELECT version_num FROM alembic_version")
                    rows = cur2.fetchall()
                    if not rows:
                        conn.exec_driver_sql("INSERT INTO alembic_version (version_num) VALUES ('a1b2c3d4e5f6')")
                    elif rows[0][0] != "a1b2c3d4e5f6":
                        conn.exec_driver_sql("UPDATE alembic_version SET version_num='a1b2c3d4e5f6'")
        except Exception:
            pass
    except Exception:
        pass
