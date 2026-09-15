from typing import Optional

from . import content, rakuten, review, selection
from .db import get_conn


def _get_or_create_product_id(product) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM products WHERE item_code = ?", (product.item_code,)
        ).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO products "
            "(item_code, name, price, review_avg, review_count, shop_name, item_url, "
            "affiliate_url, genre_id, genre_name) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                product.item_code,
                product.name,
                product.price,
                product.review_avg,
                product.review_count,
                product.shop_name,
                product.item_url,
                product.affiliate_url,
                product.genre_id,
                product.genre_name,
            ),
        )
        return cur.lastrowid


def run_cycle(keyword: str, genre_id: Optional[str] = None) -> Optional[int]:
    weights = selection.load_weights()
    candidates = rakuten.search_products(keyword=keyword, genre_id=genre_id)
    excluded = review.rejected_item_codes()
    chosen = selection.select_best(candidates, weights=weights, exclude_item_codes=excluded)
    if chosen is None:
        return None

    product_id = _get_or_create_product_id(chosen)
    text, angle = content.build_post_text(
        chosen, weights=weights, exclude_angle=review.last_used_angle()
    )
    return review.create_draft(product_id, text, angle)
