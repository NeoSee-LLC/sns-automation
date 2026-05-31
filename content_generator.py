import anthropic
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

LINE_URL = "https://lin.ee/Spj62DL"

PRODUCT_INFO = """
商品名: MSMB10K（半固体電池搭載モバイルバッテリー）
販売元: NeoSee合同会社 / ブランド: MottoS
販売予定: Amazon（2026年夏〜）

主な特徴:
- 半固体電池採用：発火・液漏れ・熱暴走のリスクを根本から低減
- 最大35W出力：MacBook Airへの給電に対応
- マグネット吸着ワイヤレス充電：最大15W
- Type-C内蔵ケーブル搭載
- 10,000mAh / 212g / 厚さ21.2mm
- 約1,000回の充放電（従来製品の約2倍）
- LCD画面で残量を1%単位で表示
- iPhone約2回フル充電可能
- 販売予定価格：¥9,800
"""

PHASES = {
    "crowdfunding": {
        "description": "クラファン訴求期（〜5/31）",
        "themes": ["安全性", "スペック", "社会的証明", "緊急訴求"],
        "cta": f"今すぐGreenfundingで支援する→ https://greenfunding.jp/neosee/projects/9225"
    },
    "production": {
        "description": "製造・出荷準備期（6月）",
        "themes": ["製造の舞台裏", "品質へのこだわり", "Amazon販売予告", "半固体電池の安全性"],
        "cta": f"Amazon販売開始を一番早くお知らせ！LINEを登録してね→ {LINE_URL}"
    },
    "delivery": {
        "description": "出荷・レビュー期（7月〜）",
        "themes": ["購入者の声・レビュー", "使用シーン紹介", "活用法・Tips", "安全性の実感"],
        "cta": f"Amazon販売中！詳細はLINEで→ {LINE_URL}"
    },
    "brand": {
        "description": "ブランド構築期（8月〜）",
        "themes": ["ライフスタイル提案", "ユーザーストーリー", "製品哲学", "安心・安全な暮らし"],
        "cta": f"MottoS公式LINEで最新情報をゲット→ {LINE_URL}"
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

INSTAGRAM_STYLES = [
    "共感型（日常の不安や悩みに寄り添う）",
    "ストーリー型（使用シーンを描写）",
    "教育型（半固体電池の仕組みや安全性を解説）",
    "比較型（従来製品との違いを具体的に）",
    "ライフスタイル型（どんな人の生活を変えるか）",
    "期待感醸成型（発売を楽しみにしてもらう）",
]

INSTAGRAM_HASHTAGS = {
    "crowdfunding": [
        "#モバイルバッテリー", "#半固体電池", "#クラウドファンディング",
        "#ガジェット", "#ガジェット好き", "#充電器", "#スマホアクセサリー",
        "#Greenfunding", "#新製品", "#テック", "#安全", "#防災グッズ",
        "#MacBook充電", "#ワイヤレス充電", "#旅行グッズ",
        "#仕事道具", "#電池", "#環境に優しい", "#NeoSee", "#MottoS",
    ],
    "production": [
        "#モバイルバッテリー", "#半固体電池", "#ガジェット", "#新製品",
        "#製造", "#品質", "#メイドインジャパン", "#テック", "#NeoSee", "#MottoS",
        "#充電器", "#スマホアクセサリー", "#ガジェット好き",
        "#Amazon", "#もうすぐ販売", "#安全", "#防災グッズ",
    ],
    "delivery": [
        "#モバイルバッテリー", "#半固体電池", "#ガジェット", "#レビュー",
        "#開封", "#ガジェット好き", "#充電器", "#スマホアクセサリー",
        "#NeoSee", "#MottoS", "#テック", "#おすすめガジェット",
        "#Amazon購入", "#ガジェットレビュー", "#安全", "#旅行グッズ",
    ],
    "brand": [
        "#モバイルバッテリー", "#半固体電池", "#ガジェット", "#ライフスタイル",
        "#安全", "#テック", "#NeoSee", "#MottoS", "#充電器",
        "#スマホアクセサリー", "#ガジェット好き", "#おすすめガジェット",
        "#Amazon", "#仕事道具", "#旅行グッズ",
    ],
}


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


def generate_instagram_caption(theme: str = None, style: str = None, supporters: int = None, days_left: int = None) -> str:
    phase = get_current_phase()
    phase_info = PHASES[phase]

    if not theme:
        theme = random.choice(phase_info["themes"])
    if not style:
        style = random.choice(INSTAGRAM_STYLES)

    context = ""
    if supporters:
        context += f"\n- 現在の支援者数: {supporters}人"
    if days_left:
        context += f"\n- 残り日数: {days_left}日"

    hashtags = random.sample(INSTAGRAM_HASHTAGS[phase], min(15, len(INSTAGRAM_HASHTAGS[phase])))
    hashtag_str = " ".join(hashtags)

    prompt = f"""あなたはInstagramマーケターです。以下の商品情報をもとに、Instagram投稿のキャプションを1つ作成してください。

【商品情報】
{PRODUCT_INFO}

【投稿条件】
- フェーズ: {phase_info['description']}
- テーマ: {theme}
- スタイル: {style}
- CTA: {phase_info['cta']}
{context}

【ルール】
- 300〜500文字程度（日本語）
- 最初の1〜2行で興味を引く（「続きを見る」より前に表示される部分）
- 適度に改行を入れて読みやすくする
- 絵文字を効果的に使う（多用しすぎない）
- 最後にCTAを入れる
- 宣伝くさくならず、価値提供を意識する
- ハッシュタグは含めない（別途追加するため）

キャプション本文のみを出力してください。ハッシュタグ・説明・前置きは不要です。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    caption_body = message.content[0].text.strip()
    return f"{caption_body}\n\n.\n.\n.\n{hashtag_str}"


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
