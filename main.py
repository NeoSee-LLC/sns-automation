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


def get_campaign_info() -> tuple:
    """支援者数と残り日数をGreenfundingページのmetaタグから取得。失敗時はデフォルト値を返す"""
    days_default = max(0, (CAMPAIGN_END_DATE - date.today()).days)
    supporters_default = 147

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        resp = requests.get(CROWDFUNDING_URL, headers=headers, timeout=10)

        supporters = supporters_default
        m = re.search(r"<meta content='(\d+)人' property='product:custom_label_1'>", resp.text)
        if m:
            supporters = int(m.group(1))
            print(f"支援者数取得成功: {supporters}人")
        else:
            print(f"支援者数スクレイピング失敗 → デフォルト {supporters_default}人を使用")

        days_left = days_default
        m = re.search(r"<meta content='(\d+)日' property='product:custom_label_0'>", resp.text)
        if m:
            days_left = int(m.group(1))
            print(f"残り日数取得成功: {days_left}日")
        else:
            print(f"残り日数スクレイピング失敗 → 計算値 {days_default}日を使用")

        return supporters, days_left

    except Exception as e:
        print(f"キャンペーン情報取得失敗: {e}")
        return supporters_default, days_default


def load_log() -> list:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(log: list):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def today_status() -> dict:
    """今日の投稿状態を返す: {'x': bool, 'instagram': bool}"""
    log = load_log()
    today_str = date.today().isoformat()
    x_ok = False
    ig_ok = False
    for entry in log:
        if entry.get("dry_run"):
            continue
        if not entry.get("datetime", "").startswith(today_str):
            continue
        if entry.get("tweet_id") and entry["tweet_id"] not in ("dry_run", "instagram_only"):
            x_ok = True
        if entry.get("instagram_success"):
            ig_ok = True
    return {"x": x_ok, "instagram": ig_ok}


def daily_post(dry_run: bool = False, instagram_only: bool = False):
    print(f"\n{'='*50}")
    mode = "Instagramのみ（リトライ）" if instagram_only else "X + Instagram"
    print(f"投稿実行 [{mode}]: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    supporters, days_left = get_campaign_info()
    print(f"支援者数: {supporters}人 / 残り: {days_left}日")

    tweet_result = {"id": "instagram_only", "text": ""}
    instagram_success = False
    instagram_caption = ""
    exit_code = 0

    # X投稿
    if not instagram_only:
        try:
            print("コンテンツを生成中...")
            tweet_text = generate_tweet(supporters=supporters, days_left=days_left)
            print(f"\n生成されたツイート:\n{tweet_text}\n")
            tweet_result = post_tweet(tweet_text, dry_run=dry_run)
        except Exception as e:
            print(f"X投稿エラー: {e}")
            exit_code = 1

    # Instagram投稿
    try:
        print("Instagramコンテンツを生成中...")
        instagram_caption = generate_instagram_caption(supporters=supporters, days_left=days_left)
        ig_index = (date.today().toordinal() + 14) % 28
        post_to_instagram(instagram_caption, image_index=ig_index, dry_run=dry_run)
        instagram_success = True
    except Exception as e:
        print(f"Instagram投稿エラー（リトライ上限到達）: {e}")
        exit_code = 1

    # ログ保存（X・Instagramそれぞれの成否を記録）
    log = load_log()
    log.append({
        "datetime": datetime.now().isoformat(),
        "phase": get_current_phase(),
        "tweet_id": tweet_result["id"],
        "text": tweet_result["text"],
        "instagram_caption": instagram_caption,
        "instagram_success": instagram_success,
        "supporters": supporters,
        "days_left": days_left,
        "dry_run": dry_run,
    })
    save_log(log)
    print(f"ログ保存完了（累計{len(log)}件）")
    print(f"結果 → X: {'✅' if tweet_result['id'] not in ('instagram_only',) else '⏭スキップ'} / Instagram: {'✅' if instagram_success else '❌失敗'}")

    if exit_code != 0:
        raise SystemExit(exit_code)


def check_and_retry():
    """今日の投稿状態を確認し、未投稿のプラットフォームにリトライする"""
    status = today_status()
    print(f"今日の投稿状態: X={'✅' if status['x'] else '❌'} / Instagram={'✅' if status['instagram'] else '❌'}")

    if status["x"] and status["instagram"]:
        print("全プラットフォームへの投稿が完了しています。")
        return

    if not status["x"] and not status["instagram"]:
        print("投稿がありません。X + Instagramに投稿します。")
        daily_post()
    elif not status["instagram"]:
        print("Instagram投稿のみ失敗しています。Instagramのみリトライします。")
        daily_post(instagram_only=True)


def run_scheduler(dry_run: bool = False):
    print(f"スケジューラー開始 / 毎日 {POST_TIME} に投稿")
    if dry_run:
        print("[DRY RUN モード：実際には投稿しません]")
    schedule.every().day.at(POST_TIME).do(daily_post, dry_run=dry_run)
    print(f"次の投稿予定: {schedule.next_run()}")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys

    if not test_connection():
        print("X APIへの接続に失敗しました。.envファイルのキーを確認してください。")
        sys.exit(1)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "schedule"
    dry_run = "--dry-run" in sys.argv

    if cmd == "now":
        daily_post(dry_run=dry_run)
    elif cmd == "instagram-only":
        daily_post(dry_run=dry_run, instagram_only=True)
    elif cmd == "check-and-retry":
        check_and_retry()
    else:
        run_scheduler(dry_run=dry_run)
