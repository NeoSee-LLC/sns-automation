import tweepy
import os
from dotenv import load_dotenv

load_dotenv()


def get_client():
    return tweepy.Client(
        bearer_token=os.getenv("X_BEARER_TOKEN"),
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
    )


def post_tweet(text: str, dry_run: bool = False) -> dict:
    if len(text) > 280:
        raise ValueError(f"ツイートが長すぎます（{len(text)}文字）。280文字以内にしてください。")

    if dry_run:
        print(f"[DRY RUN] 投稿予定のツイート:\n{text}\n文字数: {len(text)}")
        return {"id": "dry_run", "text": text}

    client = get_client()
    response = client.create_tweet(text=text)
    tweet_id = response.data["id"]
    print(f"投稿成功！ ツイートID: {tweet_id}")
    print(f"URL: https://x.com/MottoS_jp/status/{tweet_id}")
    return {"id": tweet_id, "text": text}


def test_connection() -> bool:
    try:
        client = get_client()
        me = client.get_me()
        print(f"接続成功！ アカウント: @{me.data.username}")
        return True
    except Exception as e:
        print(f"接続エラー: {e}")
        return False


if __name__ == "__main__":
    test_connection()
