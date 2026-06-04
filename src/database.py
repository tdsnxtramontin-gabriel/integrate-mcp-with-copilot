from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "school.db"
MIGRATIONS_DIR = BASE_DIR / "migrations"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def run_migrations() -> None:
    """Apply all SQL files in src/migrations exactly once."""
    if not MIGRATIONS_DIR.is_dir():
        raise FileNotFoundError(f"Migrations directory not found: {MIGRATIONS_DIR}")

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )

        applied = {
            row["filename"]
            for row in connection.execute("SELECT filename FROM schema_migrations")
        }

        for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if migration.name in applied:
                continue

            sql = migration.read_text(encoding="utf-8")
            connection.executescript(sql)
            connection.execute(
                "INSERT OR IGNORE INTO schema_migrations (filename) VALUES (?)",
                (migration.name,),
            )


def get_activities_snapshot() -> dict[str, dict[str, object]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                a.name,
                a.description,
                a.schedule,
                a.max_participants,
                s.email AS participant_email
            FROM activities a
            LEFT JOIN enrollments e ON e.activity_id = a.id
            LEFT JOIN students s ON s.id = e.student_id
            ORDER BY a.name, s.email
            """
        ).fetchall()

    activities: dict[str, dict[str, object]] = {}
    for row in rows:
        name = row["name"]
        if name not in activities:
            activities[name] = {
                "description": row["description"],
                "schedule": row["schedule"],
                "max_participants": row["max_participants"],
                "participants": [],
            }

        email = row["participant_email"]
        if email:
            activities[name]["participants"].append(email)

    return activities


def signup_student(activity_name: str, email: str) -> None:
    with get_connection() as connection:
        activity = connection.execute(
            "SELECT id FROM activities WHERE name = ?",
            (activity_name,),
        ).fetchone()

        if activity is None:
            raise LookupError("Activity not found")

        connection.execute(
            "INSERT OR IGNORE INTO students (email) VALUES (?)",
            (email,),
        )

        student = connection.execute(
            "SELECT id FROM students WHERE email = ?",
            (email,),
        ).fetchone()

        existing = connection.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE activity_id = ? AND student_id = ?
            """
            ,
            (activity["id"], student["id"]),
        ).fetchone()

        if existing:
            raise ValueError("Student is already signed up")

        connection.execute(
            "INSERT INTO enrollments (activity_id, student_id) VALUES (?, ?)",
            (activity["id"], student["id"]),
        )


def unregister_student(activity_name: str, email: str) -> None:
    with get_connection() as connection:
        activity = connection.execute(
            "SELECT id FROM activities WHERE name = ?",
            (activity_name,),
        ).fetchone()

        if activity is None:
            raise LookupError("Activity not found")

        student = connection.execute(
            "SELECT id FROM students WHERE email = ?",
            (email,),
        ).fetchone()

        if student is None:
            raise ValueError("Student is not signed up for this activity")

        deleted = connection.execute(
            "DELETE FROM enrollments WHERE activity_id = ? AND student_id = ?",
            (activity["id"], student["id"]),
        )

        if deleted.rowcount == 0:
            raise ValueError("Student is not signed up for this activity")
