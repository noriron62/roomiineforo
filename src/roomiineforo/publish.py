from . import review, threads_client
from .db import get_conn


def publish_approved() -> list:
    published = []
    for draft in review.list_approved_unpublished():
        result = threads_client.publish(draft.text)
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO posts (draft_id, threads_post_id, permalink) VALUES (?, ?, ?)",
                (draft.id, result["id"], result["permalink"]),
            )
        published.append((draft, result))
    return published
