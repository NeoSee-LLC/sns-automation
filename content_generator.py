import anthropic
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PRODUCT_INFO = """
商品名: MSMB10K（半固体電池搭載モバイルバッテリー）
販売元: NeoSee合同会社
クラファンURL: https://greenfunding.jp/neosee/projects/9225

主な特徴:
- 半固体電池採用：発火・液漏れ・熱暴走のリスクを根本から低減
- 最大35W出力：MacBook Airへの給電に対応
- マグネット吸着ワイヤレス充電：最大15W
- Type-C内蔵ケーブル搭載
- 10,000mAh / 212g / 厚さ21.2mm
- 約1,000回の充放電（従来製品の約2倍）
- LCD画面で残量を1%単位で表示
- iPhone約2回フル充電可能
- 価格：¥7,350〜（クラファン限定割引）
- 通常販売予定価格：¥9,800
"""

PHASES = {
    "crowdfunding": {
        "description": "クラファン訴求期（〜5/31）",
        "themes": ["安全性", "スペック", "社会的証明", "緊急訴求"],
        "cta": "今すぐGreenfundingで支援する→ https://greenfunding.jp/neosee/projects/9225"
    },
    "production": {
        "description": "製造・出荷準備期（6月）",
        "themes": ["製造進捗", "舞台裏レポート", "品質へのこだわり"],
        "cta": "一般販売もまもなく開始予定！フォローして情報をゲット"
    },
    "delivery": {
        "description": "出荷・レビュー期（7月〜）",
        "themes": ["購入者レビュー", "使用シーン", "活用法紹介"],
        "cta": "一般販売中→ https://greenfunding.jp/neosee/projects/9225"
    },
    "brand": {
        "description": "ブランド構築期（8月〜）",
        "themes": ["ライフスタイル提案", "ユーザーストーリー", "製品哲学"],
        "cta": "NeoSeeの安全バッテリーで、毎日をもっと安心に"
    }
}

TWEET_STYLES = [
    "問いかけ型（読者に質問する）",
    "データ・数字で驚かせる型",
    "ビフォーアフター比較型",
    "ストーリー型（体験談風）",
    "リスト型（箇条書きで特徴を伝える）",
    "緊急性・希少性を訴える型",
]


def get_current_phase():
    today = datetime.now()
    month = today.month
    if month <= 5:
        return "crowdfunding"
    elif month == 6:
        return "production"
    elif month == 7:
        return "delivery"
    else:
        return "brand"


def generate_tweet(theme: str = None, style: str = None, supporters: int = None, days_left: int = None) -> str:
    phase = get_current_phase()
    phase_info = PHASES[phase]

    if not theme:
        theme = random.choice(phase_info["themes"])
    if not style:
        style = random.choice(TWEET_STYLES)

    context = ""
    if supporters:
        context += f"\n- 現在の支援者数: {supporters}人"
    if days_left:
        context += f"\n- 残り日数: {days_left}日"

    prompt = f"""あなたはSNSマーケターです。以下の商品情報をもとに、X（Twitter）投稿文を1つ作成してください。

【商品情報】
{PRODUCT_INFO}

【投稿条件】
- フェーズ: {phase_info['description']}
- テーマ: {theme}
- スタイル: {style}
- CTA（行動促進）: {phase_info['cta']}
{context}

【ルール】
- 140文字以内（日本語）
- ハッシュタグを2〜3個含める（例: #モバイルバッテリー #半固体電池 #ガジェット）
- CTAは最後に自然に組み込む
- 絵文字を2〜3個使って親しみやすくする
- 宣伝くさくならないよう、価値提供を意識する

投稿文のみを出力してください。説明や前置きは不要です。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()


def generate_weekly_content(supporters: int = None, days_left: int = None) -> list:
    phase = get_current_phase()
    phase_info = PHASES[phase]
    tweets = []

    for i in range(7):
        theme = phase_info["themes"][i % len(phase_info["themes"])]
        style = TWEET_STYLES[i % len(TWEET_STYLES)]
        tweet = generate_tweet(theme=theme, style=style, supporters=supporters, days_left=days_left)
        tweets.append({
            "day": i + 1,
            "theme": theme,
            "style": style,
            "content": tweet
        })

    return tweets


if __name__ == "__main__":
    print("テスト投稿を生成中...\n")
    tweet = generate_tweet(supporters=137, days_left=26)
    print(f"生成されたツイート:\n{tweet}")
    print(f"\n文字数: {len(tweet)}文字")
