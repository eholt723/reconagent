import json
import logging

import aiosqlite

from app.config import settings

logger = logging.getLogger(__name__)


async def init_db() -> None:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS research_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                report TEXT,
                queries TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()
    logger.info("Database initialized at %s", settings.database_path)


async def save_run(topic: str, report: str, queries: list) -> int:
    async with aiosqlite.connect(settings.database_path) as db:
        cursor = await db.execute(
            "INSERT INTO research_runs (topic, report, queries) VALUES (?, ?, ?)",
            (topic, report, json.dumps(queries)),
        )
        await db.commit()
        return cursor.lastrowid


async def get_history(limit: int = 20) -> list:
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, topic, report, queries, created_at "
            "FROM research_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "topic": row["topic"],
                    "report": row["report"],
                    "queries": json.loads(row["queries"]) if row["queries"] else [],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
