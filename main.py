import schedule
import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from content_generator import generate_tweet, get_current_phase
from twitter_poster import post_tweet, test_connection

load_dotenv()

LOG_FILE = "post_log.json"

POST_TIME = "09:00"

SUPPORTERS_COUNT = 137
DAYS_LEFT = 26


def load_log() -> list:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(log: list):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def daily_post(dry_run: bool = False):
    print(f"\n{'='*50}")
    print(f"投稿実行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    try:
        print("コンテンツを生成中...")
        tweet_text = generate_tweet(
            supporters=SUPPORTERS_COUNT,
            days_left=DAYS_LEFT
        )
        print(f"\n生成されたツイート:\n{tweet_text}\n")

        result = post_tweet(tweet_text, dry_run=dry_run)

        log = load_log()
        log.append({
            "datetime": datetime.now().isoformat(),
            "phase": get_current_phase(),
            "tweet_id": result["id"],
            "text": result["text"],
            "dry_run": dry_run
        })
        save_log(log)

        print(f"ログ保存完了（累計{len(log)}件）")

    except Exception as e:
        print(f"エラーが発生しました: {e}")


def run_scheduler(dry_run: bool = False):
    print(f"スケジューラー開始")
    print(f"毎日 {POST_TIME} に投稿します")
    if dry_run:
        print("[DRY RUN モード：実際には投稿しません]")

    schedule.every().day.at(POST_TIME).do(daily_post, dry_run=dry_run)

    print(f"\n次の投稿予定: {schedule.next_run()}")
    print("Ctrl+C で停止できます\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


def run_now(dry_run: bool = False):
    print("今すぐ投稿を実行します...")
    daily_post(dry_run=dry_run)


if __name__ == "__main__":
    import sys

    if not test_connection():
        print("X APIへの接続に失敗しました。.envファイルのキーを確認してください。")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "now":
        dry_run = "--dry-run" in sys.argv
        run_now(dry_run=dry_run)
    else:
        dry_run = "--dry-run" in sys.argv
        run_scheduler(dry_run=dry_run)
