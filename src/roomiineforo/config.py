import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

REPO_ROOT = Path(__file__).resolve().parents[2]

RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID", "")
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID", "")
RAKUTEN_DRY_RUN = not RAKUTEN_APP_ID

THREADS_ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "")
THREADS_USER_ID = os.environ.get("THREADS_USER_ID", "")
THREADS_DRY_RUN = not (THREADS_ACCESS_TOKEN and THREADS_USER_ID)

DB_PATH = Path(os.environ.get("ROOMIINEFORO_DB_PATH", REPO_ROOT / "data" / "roomiineforo.db"))
WEIGHTS_PATH = Path(os.environ.get("ROOMIINEFORO_WEIGHTS_PATH", REPO_ROOT / "data" / "weights.json"))
FIXTURE_PRODUCTS_PATH = REPO_ROOT / "fixtures" / "sample_products.json"

THREADS_MAX_CHARS = 500
