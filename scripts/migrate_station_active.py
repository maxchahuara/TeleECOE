#!/usr/bin/env python3
"""Agrega estado activo/inactivo a estaciones existentes."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("TELEECOE_DB_PATH", PROJECT_DIR / "evaluaciones.db"))


def column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"database_not_found={DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if column_exists(cursor, "estacion", "activa"):
            print("station_active_column_exists=true")
            return

        cursor.execute("ALTER TABLE estacion ADD COLUMN activa BOOLEAN NOT NULL DEFAULT 1")
        cursor.execute("UPDATE estacion SET activa = 1 WHERE activa IS NULL")
        conn.commit()
        print("station_active_column_added=true")


if __name__ == "__main__":
    main()
