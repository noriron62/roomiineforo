import random
from collections import Counter

from roomiineforo import config
from roomiineforo.content import ANGLE_BUILDERS, build_post_text, choose_angle
from roomiineforo.models import Product


def make_product(**overrides) -> Product:
    base = dict(
        item_code="code1",
        name="テスト商品",
        price=1980,
        review_avg=4.5,
        review_count=100,
        shop_name="shop",
        item_url="https://example.com",
        genre_id="g0",
        genre_name="生活雑貨",
        affiliate_url="https://example.com/aff?scid=af1",
    )
    base.update(overrides)
    return Product(**base)


def test_post_includes_affiliate_link_and_price():
    product = make_product()
    text, angle = build_post_text(product, angle_key="pain_point")
    assert angle == "pain_point"
    assert product.affiliate_url in text
    assert "1980円" in text
    assert product.name in text


def test_post_respects_threads_char_limit():
    product = make_product(name="長い商品名" * 200)
    for angle_key in ANGLE_BUILDERS:
        text, _ = build_post_text(product, angle_key=angle_key)
        assert len(text) <= config.THREADS_MAX_CHARS


def test_different_angles_produce_different_text():
    product = make_product()
    texts = {key: build_post_text(product, angle_key=key)[0] for key in ANGLE_BUILDERS}
    assert len(set(texts.values())) == len(ANGLE_BUILDERS)


def test_choose_angle_avoids_excluded_when_possible():
    random.seed(0)
    keys = list(ANGLE_BUILDERS.keys())
    excluded = keys[0]
    results = {choose_angle(weights={"angle_weights": {}}, exclude=excluded) for _ in range(30)}
    assert excluded not in results


def test_choose_angle_prefers_higher_weight():
    random.seed(1)
    keys = list(ANGLE_BUILDERS.keys())
    weights = {"angle_weights": {keys[0]: 50.0}}
    counts = Counter(choose_angle(weights=weights) for _ in range(200))
    assert counts[keys[0]] > 150
