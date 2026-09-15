import json
import math
from typing import Iterable, Optional

from . import config
from .models import Product


def load_weights() -> dict:
    with open(config.WEIGHTS_PATH, encoding="utf-8") as f:
        weights = json.load(f)
    weights.setdefault("genre_weights", {})
    weights.setdefault("angle_weights", {})
    return weights


def save_weights(weights: dict) -> None:
    with open(config.WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(weights, f, ensure_ascii=False, indent=2)


def price_fit(price: int, weights: dict) -> float:
    lo, hi = weights["target_price_min"], weights["target_price_max"]
    if lo <= price <= hi:
        return 1.0
    distance = min(abs(price - lo), abs(price - hi))
    return max(0.0, 1.0 - distance / hi)


def score_product(product: Product, weights: dict) -> float:
    genre_weight = weights.get("genre_weights", {}).get(product.genre_id, 0.0)
    return (
        product.review_avg * weights["review_avg_weight"]
        + math.log1p(product.review_count) * weights["review_count_weight"]
        + price_fit(product.price, weights) * weights["price_fit_weight"]
        + genre_weight
    )


def select_best(
    products: Iterable[Product],
    weights: Optional[dict] = None,
    exclude_item_codes: Iterable[str] = (),
) -> Optional[Product]:
    weights = weights or load_weights()
    excluded = set(exclude_item_codes)
    candidates = [p for p in products if p.item_code not in excluded]
    if not candidates:
        return None
    return max(candidates, key=lambda p: score_product(p, weights))
