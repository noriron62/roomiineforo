import json
from typing import List, Optional

import requests

from . import config
from .models import Product

SEARCH_URL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"


def search_products(keyword: str, genre_id: Optional[str] = None, hits: int = 30) -> List[Product]:
    if config.RAKUTEN_DRY_RUN:
        return _search_products_fixture(keyword, genre_id, hits)
    return _search_products_live(keyword, genre_id, hits)


def _search_products_fixture(keyword: str, genre_id: Optional[str], hits: int) -> List[Product]:
    with open(config.FIXTURE_PRODUCTS_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    products = [
        Product(
            item_code=item["item_code"],
            name=item["name"],
            price=item["price"],
            review_avg=item["review_avg"],
            review_count=item["review_count"],
            shop_name=item["shop_name"],
            item_url=item["item_url"],
            genre_id=item["genre_id"],
            genre_name=item.get("genre_name", ""),
            affiliate_url=item["item_url"] + "?scid=af_dryrun",
        )
        for item in raw
    ]
    if genre_id:
        products = [p for p in products if p.genre_id == genre_id]
    return products[:hits]


def _search_products_live(keyword: str, genre_id: Optional[str], hits: int) -> List[Product]:
    params = {
        "applicationId": config.RAKUTEN_APP_ID,
        "keyword": keyword,
        "hits": hits,
        "sort": "-reviewCount",
        "format": "json",
    }
    if config.RAKUTEN_AFFILIATE_ID:
        params["affiliateId"] = config.RAKUTEN_AFFILIATE_ID
    if genre_id:
        params["genreId"] = genre_id

    resp = requests.get(SEARCH_URL, params=params, timeout=10)
    resp.raise_for_status()
    payload = resp.json()

    products = []
    for entry in payload.get("Items", []):
        item = entry["Item"]
        products.append(
            Product(
                item_code=item["itemCode"],
                name=item["itemName"],
                price=item["itemPrice"],
                review_avg=item.get("reviewAverage", 0.0),
                review_count=item.get("reviewCount", 0),
                shop_name=item.get("shopName", ""),
                item_url=item["itemUrl"],
                genre_id=str(item.get("genreId", genre_id or "")),
                affiliate_url=item.get("affiliateUrl") or item["itemUrl"],
            )
        )
    return products
