from roomiineforo.models import Product
from roomiineforo.selection import score_product, select_best

WEIGHTS = {
    "review_avg_weight": 1.0,
    "review_count_weight": 0.5,
    "price_fit_weight": 0.3,
    "genre_weights": {"g1": 1.5},
    "target_price_min": 1000,
    "target_price_max": 3000,
}


def make_product(**overrides) -> Product:
    base = dict(
        item_code="code1",
        name="test product",
        price=2000,
        review_avg=4.0,
        review_count=100,
        shop_name="shop",
        item_url="https://example.com",
        genre_id="g0",
        affiliate_url="https://example.com/aff",
    )
    base.update(overrides)
    return Product(**base)


def test_genre_weight_boosts_score():
    plain = make_product(genre_id="g0")
    boosted = make_product(item_code="code2", genre_id="g1")
    assert score_product(boosted, WEIGHTS) > score_product(plain, WEIGHTS)


def test_price_out_of_range_lowers_score():
    in_range = make_product(price=2000)
    out_of_range = make_product(item_code="code2", price=9000)
    assert score_product(in_range, WEIGHTS) > score_product(out_of_range, WEIGHTS)


def test_select_best_excludes_rejected():
    a = make_product(item_code="a", review_avg=4.9)
    b = make_product(item_code="b", review_avg=3.0)
    chosen = select_best([a, b], WEIGHTS, exclude_item_codes=["a"])
    assert chosen.item_code == "b"


def test_select_best_returns_none_when_all_excluded():
    a = make_product(item_code="a")
    assert select_best([a], WEIGHTS, exclude_item_codes=["a"]) is None
