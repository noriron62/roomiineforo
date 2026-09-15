import uuid
from typing import Optional

import requests

from . import config

GRAPH_BASE = "https://graph.threads.net/v1.0"


def publish(text: str) -> dict:
    if config.THREADS_DRY_RUN:
        fake_id = f"dryrun-{uuid.uuid4().hex[:10]}"
        return {"id": fake_id, "permalink": f"https://www.threads.net/dryrun/{fake_id}"}
    return _publish_live(text)


def _publish_live(text: str) -> dict:
    create_resp = requests.post(
        f"{GRAPH_BASE}/{config.THREADS_USER_ID}/threads",
        data={
            "media_type": "TEXT",
            "text": text,
            "access_token": config.THREADS_ACCESS_TOKEN,
        },
        timeout=15,
    )
    create_resp.raise_for_status()
    creation_id = create_resp.json()["id"]

    publish_resp = requests.post(
        f"{GRAPH_BASE}/{config.THREADS_USER_ID}/threads_publish",
        data={
            "creation_id": creation_id,
            "access_token": config.THREADS_ACCESS_TOKEN,
        },
        timeout=15,
    )
    publish_resp.raise_for_status()
    post_id = publish_resp.json()["id"]

    permalink = _fetch_permalink(post_id) or f"https://www.threads.net/t/{post_id}"
    return {"id": post_id, "permalink": permalink}


def _fetch_permalink(post_id: str) -> Optional[str]:
    resp = requests.get(
        f"{GRAPH_BASE}/{post_id}",
        params={"fields": "permalink", "access_token": config.THREADS_ACCESS_TOKEN},
        timeout=15,
    )
    if resp.ok:
        return resp.json().get("permalink")
    return None


def get_insights(post_id: str) -> dict:
    if config.THREADS_DRY_RUN:
        return {"likes": 0, "replies": 0, "reposts": 0, "views": 0}
    return _get_insights_live(post_id)


def _get_insights_live(post_id: str) -> dict:
    resp = requests.get(
        f"{GRAPH_BASE}/{post_id}/insights",
        params={
            "metric": "likes,replies,reposts,views",
            "access_token": config.THREADS_ACCESS_TOKEN,
        },
        timeout=15,
    )
    resp.raise_for_status()
    metrics = {}
    for entry in resp.json().get("data", []):
        name = entry["name"]
        values = entry.get("values", [])
        metrics[name] = values[0]["value"] if values else 0
    return {
        "likes": metrics.get("likes", 0),
        "replies": metrics.get("replies", 0),
        "reposts": metrics.get("reposts", 0),
        "views": metrics.get("views", 0),
    }
