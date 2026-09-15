from collections import defaultdict

from .db import get_conn
from .selection import load_weights, save_weights

WEIGHT_SCALE = 2.0

GENRE_QUERY = """
    SELECT pr.genre_id AS group_key, m.likes, m.replies, m.reposts
    FROM metrics m
    JOIN posts po ON po.id = m.post_id
    JOIN drafts d ON d.id = po.draft_id
    JOIN products pr ON pr.id = d.product_id
"""

ANGLE_QUERY = """
    SELECT d.angle AS group_key, m.likes, m.replies, m.reposts
    FROM metrics m
    JOIN posts po ON po.id = m.post_id
    JOIN drafts d ON d.id = po.draft_id
    WHERE d.angle != ''
"""


def _engagement_score(row) -> float:
    return row["likes"] + row["replies"] * 2 + row["reposts"] * 3


def _normalized_weights(rows) -> dict:
    totals = defaultdict(list)
    for row in rows:
        totals[row["group_key"]].append(_engagement_score(row))
    if not totals:
        return {}

    averages = {key: sum(scores) / len(scores) for key, scores in totals.items()}
    overall_avg = sum(averages.values()) / len(averages)
    max_deviation = max((abs(v - overall_avg) for v in averages.values()), default=1.0) or 1.0

    return {
        key: round((avg - overall_avg) / max_deviation * WEIGHT_SCALE, 3)
        for key, avg in averages.items()
    }


def recompute_weights() -> dict:
    weights = load_weights()
    with get_conn() as conn:
        genre_rows = conn.execute(GENRE_QUERY).fetchall()
        angle_rows = conn.execute(ANGLE_QUERY).fetchall()

    genre_result = _normalized_weights(genre_rows)
    if genre_result:
        weights["genre_weights"] = {**weights.get("genre_weights", {}), **genre_result}

    angle_result = _normalized_weights(angle_rows)
    if angle_result:
        weights["angle_weights"] = {**weights.get("angle_weights", {}), **angle_result}

    save_weights(weights)
    return weights
