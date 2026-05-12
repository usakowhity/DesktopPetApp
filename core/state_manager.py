# core/state_manager.py

import json
import time
from pathlib import Path
import threading

import pygame
from utils.normalize import normalize_text


class StateManager:
    """
    状態管理（p1 → n1 の直後は笑顔検出を2秒無効化）
    p1 では Whisper を pause しない（声掛け有効）
    """

    def __init__(self, pet_manager, command_parser, media_manager):
        self.pet_manager = pet_manager
        self.command_parser = command_parser
        self.media_manager = media_manager

        self.current_state = None

        now = time.time()
        self.last_interaction_time = now
        self.state_enter_time = now

        self.skip_n1_idle_until = 0
        self.last_smile_time = 0  # ← 笑顔クールダウン用

        # pending state
        self._pending_state = None
        self._pending_state_requested_at = None
        self._applying_state = False

        # whisper pause watchdog
        self._whisper_paused_by_state = False
        self._whisper_pause_at = None

        self.commands_by_state = self._load_commands()
        self.pet_aliases = self._load_pet_aliases()

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        print("[StateManager] alias 読み込み完了")

    # ---------------------------------------------------------
    def _load_commands(self):
        path = Path("data") / "commands.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            print("[StateManager] commands.json 読み込み失敗")
            return {}

    def _load_pet_aliases(self):
        path = Path("data") / "pets_alias.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except:
            print("[StateManager] pets_alias.json 読み込み失敗")
            return {}

        alias_map = {}
        for pet, aliases in raw.items():
            alias_map[pet] = [normalize_text(a) for a in aliases]
        return alias_map

    # ---------------------------------------------------------
    def _play_bark_if_needed(self, new_state):
        if new_state != "p2":
            return
        try:
            bark_path = self.pet_manager.get_bark_sound()
            if not bark_path:
                return
            sound = pygame.mixer.Sound(bark_path)
            sound.play()
            print(f"[Audio] bark 再生: {bark_path}")
        except Exception as e:
            print("[Audio] bark 再生失敗:", e)

    # ---------------------------------------------------------
    # ★ Whisper pause/resume の仕様変更
    #   p1 → pause しない
    #   p2 → pause する
    #   それ以外 → resume
    # ---------------------------------------------------------
    def _update_whisper_pause_resume(self, new_state):
        engine = getattr(self.pet_manager, "engine", None)
        if engine is None:
            return

        try:
            if new_state == "p2":
                print("[StateManager] calling engine.pause_listen()")
                engine.pause_listen()
                self._whisper_paused_by_state = True
                self._whisper_pause_at = time.time()
            else:
                print("[StateManager] calling engine.resume_listen()")
                engine.resume_listen()
                self._whisper_paused_by_state = False
                self._whisper_pause_at = None

        except Exception as e:
            print("[StateManager] whisper pause/resume error:", e)

    # ---------------------------------------------------------
    def change_state(self, new_state):
        old = self.current_state
        self.current_state = new_state
        self.state_enter_time = time.time()

        self._pending_state = new_state
        self._pending_state_requested_at = time.time()

        print(f"[State] {old} → {new_state} (pending)")

        if new_state == "n1":
            self.last_interaction_time = time.time()

    # ---------------------------------------------------------
    def _apply_pending_state(self):
        if self._pending_state is None:
            return
        if self._applying_state:
            return

        new_state = self._pending_state
        self._applying_state = True

        def _worker():
            try:
                print(f"[StateManager] media_manager.set_state THREAD START ({new_state})")
                self.media_manager.set_state(new_state)
                print(f"[StateManager] media_manager.set_state THREAD DONE ({new_state})")
            except Exception as e:
                print("[StateManager] media_manager.set_state THREAD ERROR:", e)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        t.join(timeout=1.5)

        if t.is_alive():
            print(f"[StateManager] media_manager.set_state still running after timeout for {new_state}")
            self._applying_state = False
            return

        try:
            self._play_bark_if_needed(new_state)
            self._update_whisper_pause_resume(new_state)
        except Exception as e:
            print("[StateManager] post-set_state actions error:", e)

        self._pending_state = None
        self._pending_state_requested_at = None
        self._applying_state = False

    # ---------------------------------------------------------
    def on_voice_command(self, text, engine="whisper"):
        print(f"[DEBUG] on_voice_command({engine}): '{text}'")

        now = time.time()
        self.last_interaction_time = now

        replace_map = {
            "黒": "くろ",
            "白": "しろ",
            "太郎": "たろう",
            "次郎": "じろう",
            "丸": "まる",
            "玉": "たま",
        }
        for k, v in replace_map.items():
            if k in text:
                text = text.replace(k, v)

        norm = normalize_text(text)
        print(f"[DEBUG] normalized: '{norm}'")
        if not norm:
            return

        # ペット名判定
        for pet, alias_list in self.pet_aliases.items():
            for a in alias_list:
                if norm.startswith(a) or a in norm:
                    if pet != self.pet_manager.current_pet:
                        print(f"[Pet] 他ペット名 → {pet}")
                        old = self.pet_manager.current_pet
                        self.pet_manager.set_current_pet(pet)
                        print(f"[PetManager] ペット切替: {old} → {pet}")
                        self.skip_n1_idle_until = time.time() + 5
                        self.change_state("n1")
                        return

                    print(f"[Pet] 呼びかけ → p2")
                    self.change_state("p2")
                    return

        # コマンド判定
        if self.current_state:
            cmds = self.commands_by_state.get(self.current_state, {})
            for key, next_state in cmds.items():
                if norm.startswith(key) or key in norm:
                    print(f"[Command] '{norm}' → {next_state}")
                    self.change_state(next_state)
                    return

        if hasattr(self.command_parser, "handle"):
            try:
                self.command_parser.handle(norm, self.current_state, self)
            except Exception as e:
                print("[StateManager] command_parser.handle error:", e)

    # ---------------------------------------------------------
    def on_camera_event(self, event):
        if event == "smile":
            # ★ 笑顔は n1 のときだけ有効
            if self.current_state != "n1":
                return

            now = time.time()
            # ★ クールダウン（2秒）
            if now - self.last_smile_time < 2.0:
                return

            self.last_smile_time = now
            print("[CameraEvent] smile → p1")
            self.change_state("p1")

    # ---------------------------------------------------------
    def update(self):
        now = time.time()

        self._apply_pending_state()

        # whisper watchdog
        if self._whisper_paused_by_state:
            engine = getattr(self.pet_manager, "engine", None)
            if engine and self._whisper_pause_at:
                if now - self._whisper_pause_at > 6.0:
                    print("[StateManager] watchdog: resuming whisper after timeout")
                    engine.resume_listen()
                    self._whisper_paused_by_state = False
                    self._whisper_pause_at = None

        # EOF（動画）
        if self.media_manager.has_ended():
            s = self.current_state
            print(f"[StateManager] {s} EOF → n1")
            self.change_state("n1")
            self.media_manager.clear_ended()

        # ---------------------------------------------------------
        # ★ p1（静止画）は 4 秒後に n1 に戻す
        #    その直後に last_smile_time を更新して笑顔検出を 2 秒無効化
        # ---------------------------------------------------------
        if self.current_state == "p1" and not self.media_manager.current_is_video:
            if now - self.state_enter_time >= 4:
                print("[StateManager] p1 (image) → 4秒経過 → n1")
                self.last_smile_time = time.time()  # ← ここが重要
                self.change_state("n1")
                return

        # n1 → n3（15秒無反応）
        if self.current_state == "n1":
            if now < self.skip_n1_idle_until:
                return
            if now - self.last_interaction_time >= 15:
                print("[StateManager] n1 → 15秒無反応 → n3")
                self.change_state("n3")
                return

        # n3 → n1（4秒）
        if self.current_state == "n3":
            if now - self.state_enter_time >= 4:
                print("[StateManager] n3 → 4秒経過 → n1")
                self.change_state("n1")
                return

        # p2（静止画）→ 4秒後 n1
        if self.current_state == "p2" and not self.media_manager.current_is_video:
            if now - self.state_enter_time >= 4:
                print("[StateManager] p2 → 4秒経過 → n1")
                self.change_state("n1")
                return
