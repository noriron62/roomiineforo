import argparse

from . import analytics, content, db, improve, pipeline, publish, review
from .db import get_conn


def cmd_init_db(_args):
    db.init_db()
    print(f"initialized db at {db.config.DB_PATH}")


def cmd_run_cycle(args):
    db.init_db()
    draft_id = pipeline.run_cycle(keyword=args.keyword, genre_id=args.genre_id)
    if draft_id is None:
        print("該当する候補商品がありませんでした")
    else:
        print(f"下書きを作成しました: draft_id={draft_id} (review list で確認してください)")


def cmd_review_list(_args):
    for draft in review.list_pending():
        with get_conn() as conn:
            product = conn.execute(
                "SELECT name, price FROM products WHERE id = ?", (draft.product_id,)
            ).fetchone()
        angle_label = content.ANGLE_LABELS.get(draft.angle, draft.angle)
        print(f"--- draft {draft.id} ({product['name']} / {product['price']}円) [{angle_label}] ---")
        print(draft.text)
        print()


def cmd_review_approve(args):
    review.approve(args.draft_id, note=args.note)
    print(f"draft {args.draft_id} を承認しました")


def cmd_review_reject(args):
    review.reject(args.draft_id, reason=args.reason)
    print(f"draft {args.draft_id} を却下しました")


def cmd_publish(_args):
    published = publish.publish_approved()
    if not published:
        print("投稿可能な承認済み下書きはありません")
    for draft, result in published:
        print(f"投稿しました: draft {draft.id} -> {result['permalink']}")


def cmd_collect_metrics(args):
    count = analytics.collect_metrics_for_recent_posts(hours=args.hours)
    print(f"{count}件のインサイトを記録しました")


def cmd_improve(_args):
    weights = improve.recompute_weights()
    print("重みを更新しました:")
    print(weights)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="roomiineforo")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db").set_defaults(func=cmd_init_db)

    p = sub.add_parser("run-cycle", help="商品リサーチ→選定→投稿作成をまとめて実行")
    p.add_argument("--keyword", required=True)
    p.add_argument("--genre-id", default=None)
    p.set_defaults(func=cmd_run_cycle)

    review_parser = sub.add_parser("review")
    review_sub = review_parser.add_subparsers(dest="review_command", required=True)

    review_sub.add_parser("list").set_defaults(func=cmd_review_list)

    approve_p = review_sub.add_parser("approve")
    approve_p.add_argument("draft_id", type=int)
    approve_p.add_argument("--note", default=None)
    approve_p.set_defaults(func=cmd_review_approve)

    reject_p = review_sub.add_parser("reject")
    reject_p.add_argument("draft_id", type=int)
    reject_p.add_argument("--reason", default=None)
    reject_p.set_defaults(func=cmd_review_reject)

    sub.add_parser("publish").set_defaults(func=cmd_publish)

    metrics_p = sub.add_parser("collect-metrics")
    metrics_p.add_argument("--hours", type=int, default=24)
    metrics_p.set_defaults(func=cmd_collect_metrics)

    sub.add_parser("improve").set_defaults(func=cmd_improve)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
