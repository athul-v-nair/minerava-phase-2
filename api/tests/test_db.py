import sqlite3

from app.core.database import DATABASE_URL, _db_path_from_url


def test_db_file_exists_and_wal():
    db_path = _db_path_from_url(DATABASE_URL)
    assert db_path is not None
    assert db_path.exists(), f"DB file missing at {db_path}"
    conn = sqlite3.connect(str(db_path))
    try:
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        assert mode == "wal", f"expected WAL, got {mode}"
        # alembic_version must exist after upgrade head
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        tables = [r[0] for r in rows]
        assert "alembic_version" in tables
    finally:
        conn.close()
