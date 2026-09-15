from roomiineforo import config
from roomiineforo.content import build_post_text
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
        affiliate_url="https://example.com/aff?scid=af1",
    )
    base.update(overrides)
    return Product(**base)


def test_post_includes_affiliate_link_and_price():
    product = make_product()
    text = build_post_text(product)
    assert product.affiliate_url in text
    assert "1980円" in text
    assert product.name in text


def test_post_respects_threads_char_limit():
    product = make_product(name="長い商品名" * 200)
    text = build_post_text(product)
    assert len(text) <= config.THREADS_MAX_CHARS


def test_hook_rotates():
    product = make_product()
    text0 = build_post_text(product, hook_index=0)
    text1 = build_post_text(product, hook_index=1)
    assert text0 != text1
