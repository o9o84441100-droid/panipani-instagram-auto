"""Panipani Canva text-fit contract for all 86 curated topics.

Canva API autofill does not automatically reflow imported design text safely.
Full prompts belong in the Instagram caption; short, human-edited microcopy
belongs in the visual. New topics MUST receive manually reviewed microcopy.
"""
from daily_topics import TOPICS

MICRO_PROMPTS = {
  "メール返信": "丁寧な返信文を作る",
  "会議の議事録": "会議メモを整理する",
  "長文の要約": "要点を3つにする",
  "タスク整理": "優先順位を整理",
  "提案書の骨子": "提案書の構成を作る",
  "お礼メール": "お礼の文面を作る",
  "お断りメール": "丁寧な断り文を作る",
  "質問の整理": "質問を5つに絞る",
  "アンケート作成": "質問案を6問作る",
  "表の見出し": "表の列名を提案",
  "文章の校正": "誤字脱字を直す",
  "やさしい説明": "初心者向けに説明",
  "見出し案": "見出しを10案出す",
  "FAQ作成": "FAQを8組作る",
  "比較表": "3案を表で比較",
  "商談の準備": "商談の質問を作る",
  "プレゼン構成": "5枚の構成を作る",
  "文章を短縮": "意味を保って短縮",
  "チェックリスト": "確認項目を整理",
  "手順書作成": "手順書を作る",
  "SNS投稿案": "投稿文を3案作る",
  "動画の台本": "短い動画台本を作る",
  "ブログの導入": "冒頭の文章を作る",
  "商品説明": "商品を分かりやすく説明",
  "読者目線": "読者の疑問を探す",
  "リサーチ設計": "検索語を整理する",
  "情報の真偽確認": "証拠と出典を探す",
  "読書メモ": "読書メモを整理",
  "勉強計画": "学習計画を作る",
  "復習問題": "小テストを5問作る",
  "英語の言い換え": "やさしい英語にする",
  "英会話練習": "英会話を5往復する",
  "英単語の例文": "例文を5つ作る",
  "自己紹介文": "自己紹介文を作る",
  "応募文の整理": "強みを3つ整理する",
  "面接の練習": "面接の質問を作る",
  "目標の分解": "目標を5つに分ける",
  "週次振り返り": "成果と課題を整理",
  "習慣づくり": "7日間の計画を作る",
  "献立の相談": "献立を3つ提案",
  "旅行の準備": "持ち物リストを作る",
  "旅程の下書き": "一日の旅程を作る",
  "予算の整理": "支出を分類する",
  "予定の調整": "候補日を3つ出す",
  "催促の連絡": "確認メールを作る",
  "クレーム返信": "丁寧な返信を作る",
  "案内文の作成": "案内文を作る",
  "イベント告知": "告知文を作る",
  "スプレッドシート関数": "関数を提案する",
  "CSVの整形": "CSV列名を揃える",
  "グラフの選び方": "グラフを選ぶ",
  "数字の説明": "データの傾向を説明",
  "改善アイデア": "ムダな工程を探す",
  "引き継ぎ資料": "引き継ぎを整理",
  "優先順位づけ": "優先順位を決める",
  "企画アイデア": "企画を10案考える",
  "企画の比較": "企画案を比較する",
  "ネーミング": "名前を15案出す",
  "キャッチコピー": "一文コピーを作る",
  "SNSの分析": "投稿の反応を分析",
  "コメント返信": "自然な返信を作る",
  "ストーリーズ案": "短い投稿文を作る",
  "動画タイトル": "タイトルを考える",
  "文章の構成": "文章の順番を整理",
  "客観的な表現": "事実と意見を分ける",
  "相談の整理": "選択肢を整理する",
  "質問への回答": "結論から答える",
  "要件の整理": "依頼の要件を整理",
  "仕様書の草案": "仕様書の草案を作る",
  "バグ報告": "再現手順を整理",
  "プロンプト改善": "AI依頼を具体化",
  "AI回答の点検": "AI回答を点検",
  "役割を指定": "講師役で説明する",
  "出力形式を指定": "形式を決めて出力",
  "段階的な質問": "確認質問を3つ作る",
  "条件付きの提案": "条件に合う案を出す",
  "例文を作る": "例文を3種類作る",
  "大量テキスト分類": "文章を4分類する",
  "FAQの更新": "FAQの更新点を探す",
  "一日の計画": "今日の時間割を作る",
  "会議の質問": "質問を5つ考える",
  "議題の作成": "会議の議題を作る",
  "資料の要点": "結論と行動を抜く",
  "文章の翻訳": "自然な日本語に翻訳",
  "知識の共有": "学びを3つに整理",
  "まとめノート": "メモを見出しで整理"
}

MAX_LENGTH = {
    "HOOK": 11, "SITUATION": 10, "PROMPT": 17,
    "CAUTION": 10, "CTA": 7,
}

class CopyLayoutError(RuntimeError):
    pass

def _clean(text):
    if not isinstance(text, str):
        raise CopyLayoutError("Visual text must be a string")
    result = " ".join(text.split())
    if not result or any(ord(c) < 32 for c in result):
        raise CopyLayoutError("Empty or non-printable visual text")
    return result

def short_caution(title, warning):
    warning = _clean(warning)
    if len(warning) <= MAX_LENGTH["CAUTION"]:
        return warning
    rules = (
        ("個人情報", "個人情報に注意"), ("数字", "数値を確認"),
        ("数値", "数値を確認"), ("事実", "事実を確認"),
        ("実績", "実績を確認"), ("決定", "決定事項を確認"),
        ("条件", "条件を確認"), ("期限", "期限を確認"),
        ("日時", "日時を確認"), ("時間", "時間を確認"),
        ("原文", "原文と照合"), ("名前", "名称を確認"),
        ("引用", "出典を確認"), ("公式", "公式情報を確認"),
        ("返", "相手を確認"), ("断定", "根拠を確認"),
        ("相手", "相手に配慮"), ("約束", "約束前に確認"),
    )
    for needle, answer in rules:
        if needle in warning:
            return answer
    return "必ず自分で確認"

def make_visual_copy(title, situation, full_prompt, warning):
    title, situation, full_prompt, warning = (
        _clean(x) for x in (title, situation, full_prompt, warning)
    )
    if title not in MICRO_PROMPTS:
        raise CopyLayoutError("Unreviewed Canva visual topic: " + title)
    values = {
        "HOOK": situation,
        "SITUATION": title,
        "PROMPT": MICRO_PROMPTS[title],
        "CAUTION": short_caution(title, warning),
        "CTA": "保存して試そう",
    }
    for field, value in values.items():
        if not value or len(value) > MAX_LENGTH[field]:
            raise CopyLayoutError(
                f"{field} text too long for approved Canva design: {len(value)} characters"
            )
    return values

def validate_topic_bank():
    titles = [x[0] for x in TOPICS]
    missing = set(titles) - set(MICRO_PROMPTS)
    extra = set(MICRO_PROMPTS) - set(titles)
    if missing or extra:
        raise CopyLayoutError(
            f"Topic mapping mismatch: {len(missing)} missing, {len(extra)} orphaned"
        )
    for topic in TOPICS:
        make_visual_copy(*topic)
    return len(TOPICS)
