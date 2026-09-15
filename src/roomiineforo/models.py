from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    item_code: str
    name: str
    price: int
    review_avg: float
    review_count: int
    shop_name: str
    item_url: str
    genre_id: str
    genre_name: str = ""
    affiliate_url: str = ""
    id: Optional[int] = None


@dataclass
class Draft:
    id: int
    product_id: int
    text: str
    status: str
    reviewer_note: Optional[str]
    created_at: str


@dataclass
class Post:
    id: int
    draft_id: int
    threads_post_id: str
    permalink: str
    posted_at: str
