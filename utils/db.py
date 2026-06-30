"""SQLite 数据库工具"""

import os
import sqlite3
import uuid

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "app.db")


def _ensure_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_db():
    """获取数据库连接"""
    _ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化表"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id TEXT PRIMARY KEY,
            job_type TEXT NOT NULL,
            job_name TEXT NOT NULL,
            report TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value INTEGER DEFAULT 0
        )
    """)
    # 初始化统计数据
    for k in ("resume_count", "interview_count"):
        conn.execute("INSERT OR IGNORE INTO stats (key, value) VALUES (?, 0)", (k,))
    conn.commit()
    conn.close()


# ═════════ 面试记录 ═════════

def save_interview(job_type, job_name, report):
    """保存一条面试记录"""
    rid = uuid.uuid4().hex[:8]
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db()
    conn.execute(
        "INSERT INTO interviews (id, job_type, job_name, report, created_at) VALUES (?,?,?,?,?)",
        (rid, job_type, job_name, report, now),
    )
    conn.commit()
    conn.close()
    return rid


def list_interviews():
    """列出所有面试记录，按时间倒序"""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, job_type, job_name, created_at FROM interviews ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [{"id": r["id"], "job_type": r["job_type"], "job_name": r["job_name"], "time": r["created_at"]} for r in rows]


def get_interview(rid):
    """获取单条面试详情"""
    conn = get_db()
    row = conn.execute("SELECT * FROM interviews WHERE id = ?", (rid,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# ═════════ 统计数据 ═════════

def get_stats():
    """获取统计数据"""
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM stats").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


def increment_stat(key):
    """增加某个统计计数"""
    conn = get_db()
    conn.execute("UPDATE stats SET value = value + 1 WHERE key = ?", (key,))
    conn.commit()
    conn.close()
