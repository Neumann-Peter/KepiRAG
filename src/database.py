import sqlite3
from pathlib import Path
from typing import Optional


def get_connection(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def init_db(db_path: Path) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS images (
                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      filename TEXT NOT NULL,
                                                      full_path TEXT NOT NULL,
                                                      roi_date_path TEXT,
                                                      roi_barcode_path TEXT,
                                                      roi_seal_path TEXT,
                                                      label TEXT,
                                                      defect_type TEXT,
                                                      note TEXT,
                                                      created_at TEXT NOT NULL
                )
                """)

    conn.commit()
    conn.close()


def insert_image_record(
        db_path: Path,
        filename: str,
        full_path: str,
        roi_date_path: str,
        roi_barcode_path: str,
        roi_seal_path: str,
        label: Optional[str] = None,
        defect_type: Optional[str] = None,
        note: Optional[str] = None,
        created_at: str = "",
) -> int:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
                INSERT INTO images (
                    filename, full_path, roi_date_path, roi_barcode_path, roi_seal_path,
                    label, defect_type, note, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    filename,
                    full_path,
                    roi_date_path,
                    roi_barcode_path,
                    roi_seal_path,
                    label,
                    defect_type,
                    note,
                    created_at,
                ))

    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_image_by_id(db_path: Path, row_id: int):
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("SELECT * FROM images WHERE id = ?", (row_id,))
    row = cur.fetchone()

    conn.close()
    return row

def get_image_label_and_defect_by_id(db_path: Path, row_id: int):
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, filename, label, defect_type FROM images WHERE id = ?",
        (row_id,)
    )
    row = cur.fetchone()

    conn.close()
    return row

def update_image_label(
        db_path: Path,
        row_id: int,
        label: str,
        defect_type: str | None = None,
) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
                UPDATE images
                SET label = ?, defect_type = ?
                WHERE id = ?
                """, (label, defect_type, row_id))

    conn.commit()
    conn.close()