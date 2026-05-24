"""Lightweight SQLite migrations for new columns."""

from sqlalchemy import inspect, text

from .database import engine


def run_migrations() -> None:
    insp = inspect(engine)
    tables = insp.get_table_names()

    if "watchlist" in tables:
        cols = {c["name"] for c in insp.get_columns("watchlist")}
        with engine.begin() as conn:
            if "face_embedding" not in cols:
                conn.execute(text("ALTER TABLE watchlist ADD COLUMN face_embedding TEXT"))
            if "photo_file" not in cols:
                conn.execute(text("ALTER TABLE watchlist ADD COLUMN photo_file VARCHAR(120)"))
