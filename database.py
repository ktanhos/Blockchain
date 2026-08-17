import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "blockchain_case.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            profile_json TEXT NOT NULL,
            case01_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def save_project(project_id: str, student_id: str, profile: dict, case01: dict):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO projects(project_id, student_id, profile_json, case01_json)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(project_id) DO UPDATE SET
            student_id = excluded.student_id,
            profile_json = excluded.profile_json,
            case01_json = excluded.case01_json,
            updated_at = CURRENT_TIMESTAMP
        """,
        (project_id, student_id, json.dumps(profile, ensure_ascii=False), json.dumps(case01, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def load_project(project_id: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT student_id, profile_json, case01_json FROM projects WHERE project_id = ?",
        (project_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "student_id": row[0],
        "profile": json.loads(row[1]),
        "case01": json.loads(row[2] or "{}"),
    }
