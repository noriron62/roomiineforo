import math
import random
from dataclasses import replace
from typing import Callable, Dict, Optional

from . import config, selection
from .models import Product

FOOTER = "#PR #楽天"


def _pain_point(p: Product) -> str:
    genre = p.genre_name or "毎日のちょっとしたこと"
    return (
        f"「{genre}」で地味にストレス溜まってませんか。\n\n"
        f"それ、「{p.name}」で解決するかもしれません。\n"
        f"評価{p.review_avg}（{p.review_count}件のレビュー）、価格は{p.price}円。\n\n"
        f"{p.affiliate_url}\n"
        f"{FOOTER}"
    )


def _empathy(p: Product) -> str:
    return (
        "これ、わかる人だけわかってほしい。\n\n"
        f"「{p.name}」、使い始めてから地味に生活が変わった。\n"
        f"評価{p.review_avg}／レビュー{p.review_count}件、{p.price}円。\n\n"
        f"{p.affiliate_url}\n"
        f"{FOOTER}"
    )


def _social_proof(p: Product) -> str:
    return (
        f"レビュー{p.review_count}件で星{p.review_avg}。\n"
        "これだけの人が選んでるのには理由がある。\n\n"
        f"「{p.name}」（{p.price}円）\n\n"
        f"{p.affiliate_url}\n"
        f"{FOOTER}"
    )


def _before_after(p: Product) -> str:
    return (
        f"「{p.price}円でこれ？」と正直半信半疑だった。\n"
        "けど使ったら考えが変わった。\n\n"
        f"「{p.name}」\n"
        f"評価{p.review_avg}（{p.review_count}件のレビュー）\n\n"
        f"{p.affiliate_url}\n"
        f"{FOOTER}"
    )


def _question_hook(p: Product) -> str:
    return (
        f"「{p.name}」って知ってました？\n"
        "知らなかった自分を殴りたくなった。\n\n"
        f"評価{p.review_avg}／{p.review_count}件のレビュー、{p.price}円。\n\n"
        f"{p.affiliate_url}\n"
        f"{FOOTER}"
    )


def _cospa(p: Product) -> str:
    return (
        f"{p.price}円は正直安すぎると思ってる。\n\n"
        f"「{p.name}」\n"
        f"評価{p.review_avg}（{p.review_count}件のレビュー）\n"
        "このクオリティでこの値段はコスパ良すぎる。\n\n"
        f"{p.affiliate_url}\n"
        f"{FOOTER}"
    )


ANGLE_BUILDERS: Dict[str, Callable[[Product], str]] = {
    "pain_point": _pain_point,
    "empathy": _empathy,
    "social_proof": _social_proof,
    "before_after": _before_after,
    "question_hook": _question_hook,
    "cospa": _cospa,
}

ANGLE_LABELS = {
    "pain_point": "悩み解決型",
    "empathy": "共感・あるある型",
    "social_proof": "数字インパクト型",
    "before_after": "ビフォーアフター型",
    "question_hook": "疑問投げかけ型",
    "cospa": "コスパ訴求型",
}


def choose_angle(weights: Optional[dict] = None, exclude: Optional[str] = None) -> str:
    weights = weights or selection.load_weights()
    angle_weights = weights.get("angle_weights", {})

    keys = list(ANGLE_BUILDERS.keys())
    if exclude and len(keys) > 1:
        keys = [k for k in keys if k != exclude]

    scores = [angle_weights.get(k, 0.0) for k in keys]
    max_score = max(scores)
    exp_scores = [math.exp(s - max_score) for s in scores]
    total = sum(exp_scores)
    probs = [e / total for e in exp_scores]
    return random.choices(keys, weights=probs, k=1)[0]


def build_post_text(
    product: Product,
    angle_key: Optional[str] = None,
    weights: Optional[dict] = None,
    exclude_angle: Optional[str] = None,
) -> tuple:
    angle_key = angle_key or choose_angle(weights=weights, exclude=exclude_angle)
    builder = ANGLE_BUILDERS[angle_key]
    text = builder(product)

    if len(text) > config.THREADS_MAX_CHARS:
        overflow = len(text) - config.THREADS_MAX_CHARS
        trimmed_name = product.name[: max(0, len(product.name) - overflow - 1)] + "…"
        text = builder(replace(product, name=trimmed_name))

    return text, angle_key
