from typing import List, Optional

from .db import get_conn
from .models import Draft


def create_draft(product_id: int, text: str, angle: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO drafts (product_id, text, angle, status) VALUES (?, ?, ?, 'pending_review')",
            (product_id, text, angle),
        )
        return cur.lastrowid


def list_pending() -> List[Draft]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, product_id, text, angle, status, reviewer_note, created_at "
            "FROM drafts WHERE status = 'pending_review' ORDER BY created_at"
        ).fetchall()
    return [Draft(**dict(row)) for row in rows]


def last_used_angle() -> Optional[str]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT angle FROM drafts ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
    return row["angle"] if row else None


def approve(draft_id: int, note: Optional[str] = None) -> None:
    _set_status(draft_id, "approved", note)


def reject(draft_id: int, reason: Optional[str] = None) -> None:
    _set_status(draft_id, "rejected", reason)


def _set_status(draft_id: int, status: str, note: Optional[str]) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE drafts SET status = ?, reviewer_note = ?, reviewed_at = datetime('now') "
            "WHERE id = ?",
            (status, note, draft_id),
        )


def list_approved_unpublished() -> List[Draft]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT d.id, d.product_id, d.text, d.angle, d.status, d.reviewer_note, d.created_at "
            "FROM drafts d "
            "LEFT JOIN posts p ON p.draft_id = d.id "
            "WHERE d.status = 'approved' AND p.id IS NULL "
            "ORDER BY d.created_at"
        ).fetchall()
    return [Draft(**dict(row)) for row in rows]


def rejected_item_codes() -> List[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT pr.item_code FROM drafts d "
            "JOIN products pr ON pr.id = d.product_id "
            "WHERE d.status = 'rejected'"
        ).fetchall()
    return [row["item_code"] for row in rows]
