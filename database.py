import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "blockchain_case.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            profile_json TEXT NOT NULL,
            case01_json TEXT NOT NULL DEFAULT '{}',
            case02_json TEXT NOT NULL DEFAULT '{}',
            case03_json TEXT NOT NULL DEFAULT '{}',
            report_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(projects)").fetchall()}
    if "case02_json" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN case02_json TEXT NOT NULL DEFAULT '{}'")
    if "case03_json" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN case03_json TEXT NOT NULL DEFAULT '{}'")
    if "report_json" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN report_json TEXT NOT NULL DEFAULT '{}'")
    conn.commit()
    return conn


def save_project(project_id: str, student_id: str, profile: dict, case01: dict, case02: dict | None = None, case03: dict | None = None, report: dict | None = None):
    conn = get_connection()
    existing = conn.execute("SELECT case02_json, case03_json, report_json FROM projects WHERE project_id = ?", (project_id,)).fetchone()
    old_case02 = json.loads(existing[0] or "{}") if existing else {}
    old_case03 = json.loads(existing[1] or "{}") if existing else {}
    old_report = json.loads(existing[2] or "{}") if existing else {}
    case02 = old_case02 if case02 is None else case02
    case03 = old_case03 if case03 is None else case03
    report = old_report if report is None else report
    conn.execute("""
        INSERT INTO projects(project_id, student_id, profile_json, case01_json, case02_json, case03_json, report_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id) DO UPDATE SET
            student_id = excluded.student_id,
            profile_json = excluded.profile_json,
            case01_json = excluded.case01_json,
            case02_json = excluded.case02_json,
            case03_json = excluded.case03_json,
            report_json = excluded.report_json,
            updated_at = CURRENT_TIMESTAMP
    """, (project_id, student_id, json.dumps(profile, ensure_ascii=False), json.dumps(case01, ensure_ascii=False), json.dumps(case02, ensure_ascii=False), json.dumps(case03, ensure_ascii=False), json.dumps(report, ensure_ascii=False)))
    conn.commit()
    conn.close()


def load_project(project_id: str):
    conn = get_connection()
    row = conn.execute("SELECT student_id, profile_json, case01_json, case02_json, case03_json, report_json FROM projects WHERE project_id = ?", (project_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "student_id": row[0],
        "profile": json.loads(row[1]),
        "case01": json.loads(row[2] or "{}"),
        "case02": json.loads(row[3] or "{}"),
        "case03": json.loads(row[4] or "{}"),
        "report": json.loads(row[5] or "{}"),
    }
