from . import threads_client
from .db import get_conn


def collect_metrics_for_recent_posts(hours: int = 24) -> int:
    with get_conn() as conn:
        posts = conn.execute(
            "SELECT id, threads_post_id FROM posts "
            "WHERE posted_at >= datetime('now', ?)",
            (f"-{hours} hours",),
        ).fetchall()

    collected = 0
    for post in posts:
        metrics = threads_client.get_insights(post["threads_post_id"])
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO metrics (post_id, likes, replies, reposts, views) "
                "VALUES (?, ?, ?, ?, ?)",
                (post["id"], metrics["likes"], metrics["replies"], metrics["reposts"], metrics["views"]),
            )
        collected += 1
    return collected
