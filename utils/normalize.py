import unicodedata
import re

def kata_to_hira(text):
    return "".join(
        chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch
        for ch in text
    )

def normalize_text(text):
    if not text:
        return ""

    # 全角 → 半角
    text = unicodedata.normalize("NFKC", text)

    # カタカナ → ひらがな
    text = kata_to_hira(text)

    # 小文字化
    text = text.lower()

    # 記号除去
    text = re.sub(r"[^ぁ-んa-z0-9ー]", "", text)

    # 伸ばし棒の吸収
    text = re.sub(r"ー+", "ー", text)

    # ★ Whisper tiny の揺れ吸収
    text = text.replace("っ", "")      # くっくっ → くく
    text = text.replace("んん", "ん")  # んんん → ん
    text = text.replace("おお", "お")  # おおて → おて
    text = text.replace("こう", "こ")  # これこう → これこ
    text = text.replace("わり", "り")  # かわりこ → かわりこ → かわりこ

    # ★ お手系の吸収
    text = text.replace("おてっ", "おて")
    text = text.replace("おてー", "おて")
    text = text.replace("おてちて", "おて")
    text = text.replace("おてして", "おて")
    text = text.replace("おてちょうだい", "おて")

    return text


