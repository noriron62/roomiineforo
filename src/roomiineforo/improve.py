from collections import defaultdict

from .db import get_conn
from .selection import load_weights, save_weights

GENRE_WEIGHT_SCALE = 2.0


def _engagement_score(row) -> float:
    return row["likes"] + row["replies"] * 2 + row["reposts"] * 3


def recompute_genre_weights() -> dict:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT pr.genre_id AS genre_id, m.likes, m.replies, m.reposts
            FROM metrics m
            JOIN posts po ON po.id = m.post_id
            JOIN drafts d ON d.id = po.draft_id
            JOIN products pr ON pr.id = d.product_id
            """
        ).fetchall()

    weights = load_weights()
    if not rows:
        return weights

    totals = defaultdict(list)
    for row in rows:
        totals[row["genre_id"]].append(_engagement_score(row))

    genre_avg = {genre: sum(scores) / len(scores) for genre, scores in totals.items()}
    overall_avg = sum(genre_avg.values()) / len(genre_avg)
    max_deviation = max((abs(v - overall_avg) for v in genre_avg.values()), default=1.0) or 1.0

    genre_weights = weights.get("genre_weights", {})
    for genre, avg in genre_avg.items():
        normalized = (avg - overall_avg) / max_deviation
        genre_weights[genre] = round(normalized * GENRE_WEIGHT_SCALE, 3)

    weights["genre_weights"] = genre_weights
    save_weights(weights)
    return weights
