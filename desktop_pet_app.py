# desktop_pet_app.py

import sys
import pygame
from PySide6.QtWidgets import QApplication

from ui.pet_select_welcome import PetSelectWelcome
from core.pet_manager import PetManager
from core.state_manager import StateManager
from core.media_manager import MediaManager
from core.command_parser import CommandParser

from core.camera_manager import CameraDetector as CameraManager
from engines.whisper_engine import WhisperEngine

import sys
import os
import traceback

def setup_log():
    log_path = os.path.join(os.path.dirname(sys.argv[0]), "error_log.txt")
    sys.stderr = open(log_path, "w", encoding="utf-8")
    sys.stdout = sys.stderr
    print("[Log] Logging started:", log_path)

setup_log()


def start_desktop_pet(pet_id):
    """
    Welcome 画面でペットが選択された後に呼ばれる。
    pygame のメインループを開始する。
    """

    # -----------------------------
    # 各マネージャ初期化
    # -----------------------------
    pet_manager = PetManager()
    command_parser = CommandParser()
    media_manager = MediaManager(pet_manager)
    camera_manager = CameraManager()

    # 先に StateManager を作る（callback で使うため）
    state_manager = StateManager(pet_manager, command_parser, media_manager)

    # -----------------------------
    # WhisperEngine 初期化
    # -----------------------------
    engine = WhisperEngine()

    # WhisperEngine → StateManager の接続（正しい署名）
    def whisper_callback(text, engine="whisper"):
        try:
            state_manager.on_voice_command(text, engine)
        except Exception as e:
            print("[Main] whisper_callback error:", e)

    engine.set_callback(whisper_callback)
    engine.start()
    pet_manager.engine = engine

    # 最初のペットをセット
    pet_manager.set_current_pet(pet_id)
    state_manager.change_state("n1")

    # -----------------------------
    # pygame 初期化
    # -----------------------------
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Desktop Pet")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # -----------------------------
        # カメライベント（n1 のときだけ有効）
        # -----------------------------
        if state_manager.current_state == "n1":
            ev = camera_manager.detect()
            if ev:
                state_manager.on_camera_event(ev)


        # -----------------------------
        # 状態更新（StateManager.update 内で pending 適用を行う）
        # -----------------------------
        state_manager.update()

        # -----------------------------
        # メディアのプリロードが完了していればメインスレッドで適用する
        # -----------------------------
        try:
            applied = media_manager.apply_preloaded_state()
            if applied:
                print("[Main] applied preloaded media state")
        except Exception as e:
            print("[Main] apply_preloaded_state error:", e)

        # -----------------------------
        # 描画（例外保護＋色空間尊重）
        # -----------------------------
        screen.fill((0, 0, 0))

        frame = None
        try:
            # デバッグログ（必要なら有効化）
            # print("[DEBUG] calling media_manager.get_frame()")
            frame = media_manager.get_frame()
            # print("[DEBUG] media_manager.get_frame() returned")
        except Exception as e:
            print("[DEBUG] media_manager.get_frame() exception:", e)
            frame = None

        if frame is not None:
            import cv2
            import numpy as np

            # デバッグ：形状と先頭ピクセル（必要なら有効化）
            try:
                # print("[DEBUG] frame.shape:", frame.shape, "frame[0,0]:", frame[0,0])
                pass
            except Exception:
                pass

            # MediaManager がフレームの色空間を教えてくれるフラグを尊重する
            try:
                is_bgr = getattr(media_manager, "frame_is_bgr", True)
            except Exception:
                is_bgr = True

            try:
                if is_bgr:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    frame_rgb = frame
            except Exception:
                # 変換に失敗したら生のフレームを使う（最悪でも表示を続ける）
                frame_rgb = frame

            # numpy -> pygame surface
            try:
                surf = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            except Exception as e:
                print("[DEBUG] make_surface error:", e)
                surf = None

            if surf is not None:
                img_w, img_h = surf.get_size()
                scr_w, scr_h = screen.get_size()

                scale = min(scr_w / img_w, scr_h / img_h)
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)

                surf = pygame.transform.smoothscale(surf, (new_w, new_h))

                x = (scr_w - new_w) // 2
                y = (scr_h - new_h) // 2
                screen.blit(surf, (x, y))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    welcome = PetSelectWelcome()

    def on_pet_selected(pet_id):
        welcome.close()
        start_desktop_pet(pet_id)

    welcome.pet_selected.connect(on_pet_selected)
    welcome.show()

    sys.exit(app.exec())
