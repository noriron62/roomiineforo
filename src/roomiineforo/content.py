from . import config
from .models import Product

HOOK_TEMPLATES = [
    "これ、正直買ってよかった。",
    "気になってたやつ、ついに見つけた。",
    "地味に生活変わったアイテム。",
]


def build_post_text(product: Product, hook_index: int = 0) -> str:
    hook = HOOK_TEMPLATES[hook_index % len(HOOK_TEMPLATES)]
    body = (
        f"{hook}\n\n"
        f"「{product.name}」\n"
        f"評価{product.review_avg}（{product.review_count}件のレビュー）\n"
        f"価格: {product.price}円\n\n"
        f"{product.affiliate_url}\n"
        f"#PR #楽天"
    )
    if len(body) > config.THREADS_MAX_CHARS:
        overflow = len(body) - config.THREADS_MAX_CHARS
        trimmed_name = product.name[: max(0, len(product.name) - overflow - 1)] + "…"
        body = (
            f"{hook}\n\n"
            f"「{trimmed_name}」\n"
            f"評価{product.review_avg}（{product.review_count}件のレビュー）\n"
            f"価格: {product.price}円\n\n"
            f"{product.affiliate_url}\n"
            f"#PR #楽天"
        )
    return body
