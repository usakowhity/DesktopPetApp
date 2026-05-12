import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from utils.normalize import normalize_text


# ---------------------------------------------------------
# PyInstaller / 通常実行 両対応のパス解決
# ---------------------------------------------------------
def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return base / relative_path


# ---------------------------------------------------------
# レーベンシュタイン距離
# ---------------------------------------------------------
def levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    if len(b) == 0:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            insert = prev[j + 1] + 1
            delete = curr[j] + 1
            replace = prev[j] + (ca != cb)
            curr.append(min(insert, delete, replace))
        prev = curr
    return prev[-1]


# ---------------------------------------------------------
# CommandParser 本体
# ---------------------------------------------------------
class CommandParser:
    def __init__(self, json_path="data/commands.json", misheard_path="logs/misheard.log"):
        self.commands_path = resource_path(json_path)
        self.misheard_path = resource_path(misheard_path)

        self.commands = {}
        self.load_commands(self.commands_path)

    # ---------------------------------------------------------
    # commands.json 読み込み
    # ---------------------------------------------------------
    def load_commands(self, path: Path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.commands = json.load(f)
        else:
            print(f"[CommandParser] commands.json が見つかりません: {path}")
            self.commands = {}

    # ---------------------------------------------------------
    # ノイズ判定
    # ---------------------------------------------------------
    def is_noise_word(self, w):
        if len(w) <= 1:
            return True
        if len(w) > 12:
            return True
        if re.fullmatch(r"(.)\1{2,}", w):
            return True
        return False

    # ---------------------------------------------------------
    # misheard.log に記録
    # ---------------------------------------------------------
    def log_misheard(self, text, engine, reason):
        try:
            os.makedirs(self.misheard_path.parent, exist_ok=True)

            record = {
                "time": datetime.now().isoformat(timespec="seconds"),
                "engine": engine,
                "reason": reason,
                "text": text
            }
            with open(self.misheard_path, "a", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            print("[misheard.log] write failed:", e)

    # ---------------------------------------------------------
    # 状態遷移判定（p10 誤爆防止版）
    # ---------------------------------------------------------
    def get_state_for_command(self, text, current_state, engine="vosk"):

        # normalize
        full_norm = normalize_text(text)
        print(f"[DEBUG] normalized: '{full_norm}'")

        # ひらがな抽出
        words = re.findall(r"[ぁ-んー]+", full_norm)

        # 現在の状態の命令セット
        state_cmds = self.commands.get(current_state, {})

        # 命令語も normalize
        normalized_cmds = {
            normalize_text(cmd): state_cmds[cmd]
            for cmd in state_cmds
        }

        # -----------------------------------------------------
        # ① 単語ごとに判定
        # -----------------------------------------------------
        for w in words:
            if self.is_noise_word(w):
                continue

            for cmd_norm, next_state in normalized_cmds.items():

                # ★ p10（ちん）は完全一致のみ
                if next_state == "p10":
                    if w == cmd_norm:
                        return next_state
                    else:
                        continue

                # 完全一致
                if w == cmd_norm:
                    return next_state

                # 語頭一致
                if cmd_norm.startswith(w) and len(w) >= 2:
                    return next_state

                # 部分一致
                if w in cmd_norm and len(w) >= 2:
                    return next_state

                # 距離 ≤ 1（p10 以外）
                if levenshtein(w, cmd_norm) <= 1:
                    return next_state

        # -----------------------------------------------------
        # ② 文全体でもチェック
        # -----------------------------------------------------
        if full_norm and not self.is_noise_word(full_norm):
            for cmd_norm, next_state in normalized_cmds.items():

                # ★ p10 は完全一致のみ
                if next_state == "p10":
                    if full_norm == cmd_norm:
                        return next_state
                    else:
                        continue

                if full_norm == cmd_norm:
                    return next_state

                if levenshtein(full_norm, cmd_norm) <= 1:
                    return next_state

        # -----------------------------------------------------
        # ③ 一致なし → misheard
        # -----------------------------------------------------
        self.log_misheard(text, engine, "no_match")
        return None
