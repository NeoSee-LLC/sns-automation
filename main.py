import schedule
import time
import json
import os
import re
import requests
from datetime import datetime, date
from dotenv import load_dotenv
from content_generator import generate_tweet, generate_instagram_caption, get_current_phase
from twitter_poster import post_tweet, test_connection
from instagram_poster import post_to_instagram

load_dotenv()

LOG_FILE = "post_log.json"

POST_TIME = "09:00"

CAMPAIGN_END_DATE = date(2026, 5, 31)
CROWDFUNDING_URL = "https://greenfunding.jp/neosee/projects/9225"


def get_days_left() -> int:
    remaining = (CAMPAIGN_END_DATE - date.today()).days
    return max(0, remaining)


def get_supporters_count() -> int:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        resp = requests.get(CROWDFUNDING_URL, headers=headers, timeout=10)
        match = re.search(r'(\d[\d,]+)\s*(?:人|件).*?(?:支援|サポーター)', resp.text)
        if match:
            count = int(match.group(1).replace(",", ""))
            print(f"支援者数取得成功: {count}人")
            return count
    except Exception as e:
        print(f"支援者数取得失敗（デフォルト値を使用）: {e}")
    return 147


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
        supporters = get_supporters_count()
        days_left = get_days_left()
        print(f"支援者数: {supporters}人 / 残り: {days_left}日")

        print("コンテンツを生成中...")
        tweet_text = generate_tweet(
            supporters=supporters,
            days_left=days_left
        )
        print(f"\n生成されたツイート:\n{tweet_text}\n")

        result = post_tweet(tweet_text, dry_run=dry_run)

        print("Instagramコンテンツを生成中...")
        instagram_caption = generate_instagram_caption(
            supporters=supporters,
            days_left=days_left
        )
        ig_index = (date.today().toordinal() + 8) % 14
        post_to_instagram(instagram_caption, image_index=ig_index, dry_run=dry_run)

        log = load_log()
        log.append({
            "datetime": datetime.now().isoformat(),
            "phase": get_current_phase(),
            "tweet_id": result["id"],
            "text": result["text"],
            "instagram_caption": instagram_caption,
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
