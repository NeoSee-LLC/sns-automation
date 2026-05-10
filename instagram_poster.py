import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

IMAGE_URLS = [
    "https://raw.githubusercontent.com/NeoSee-LLC/sns-automation/main/10.png",
    "https://raw.githubusercontent.com/NeoSee-LLC/sns-automation/main/11.png",
    "https://raw.githubusercontent.com/NeoSee-LLC/sns-automation/main/12.png",
]

MAX_RETRIES = 3
RETRY_WAIT = 10  # seconds


def post_to_instagram(caption: str, image_index: int = 0, dry_run: bool = False) -> dict:
    image_url = IMAGE_URLS[image_index % len(IMAGE_URLS)]

    if dry_run:
        print(f"[DRY RUN] Instagram投稿予定:")
        print(f"画像URL: {image_url}")
        print(f"キャプション:\n{caption}")
        return {"status": "dry_run", "image_url": image_url, "caption": caption}

    payload = {
        "caption": caption,
        "image_url": image_url
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=30)
            if response.status_code == 200:
                print(f"Instagram投稿リクエスト送信成功！")
                print(f"画像URL: {image_url}")
                return {"status": "success", "image_url": image_url}
            else:
                last_error = f"ステータスコード {response.status_code}: {response.text}"
                print(f"[試行 {attempt}/{MAX_RETRIES}] Make.com Webhookエラー: {last_error}")
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"[試行 {attempt}/{MAX_RETRIES}] 通信エラー: {last_error}")

        if attempt < MAX_RETRIES:
            print(f"{RETRY_WAIT}秒後にリトライします...")
            time.sleep(RETRY_WAIT)

    raise Exception(f"Make.com Webhook が {MAX_RETRIES} 回失敗しました。最後のエラー: {last_error}")


if __name__ == "__main__":
    result = post_to_instagram(
        caption="テスト投稿です🔋 #モバイルバッテリー #半固体電池",
        dry_run=True
    )
    print(result)
