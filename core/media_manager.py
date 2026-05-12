# core/media_manager.py

import threading
import time
import cv2
import numpy as np
from pathlib import Path


class MediaManager:
    """
    MediaManager（動画判定修正版）
    - set_state(state): 非同期プリロード（動画/静止画の自動判定）
    - apply_preloaded_state(): メインスレッドで軽量適用
    - get_frame(): 毎フレーム即時返却（動画は main-thread 再生）
    """

    def __init__(self, pet_manager):
        self.pet_manager = pet_manager

        # 現在のフレーム
        self._current_frame = None
        self.frame_is_bgr = True
        self.current_is_video = False

        # 動画再生用
        self._video_cap = None

        # プリロード用
        self._preload_lock = threading.Lock()
        self._preloaded = None
        self._preloaded_is_bgr = True
        self._preloaded_is_video = False
        self._preloaded_video_path = None

        self.last_frame_time = None
        self._ended = False

    # ---------------------------------------------------------
    # public: 非同期プリロード開始
    # ---------------------------------------------------------
    def set_state(self, state):
        try:
            t = threading.Thread(target=self._preload_state, args=(state,), daemon=True)
            t.start()
        except Exception as e:
            print("[Media] set_state thread start error:", e)

    # ---------------------------------------------------------
    # 動画判定：存在チェックだけでなく「実際に読めるか」を確認する
    # ---------------------------------------------------------
    def _preload_state(self, state):
        try:
            pet = self.pet_manager.current_pet
            base = Path("assets") / pet

            video_path = base / f"{state}.mp4"
            img_png = base / f"{state}.png"
            img_jpg = base / f"{state}.jpg"

            pre = None
            is_bgr = True
            is_video = False
            pre_video_path = None

            # -----------------------------
            # 1) 動画判定（存在＋実際に読めるか）
            # -----------------------------
            if video_path.exists():
                try:
                    cap = cv2.VideoCapture(str(video_path))
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # 正常に動画として読めた
                        pre = frame.copy()
                        is_bgr = True
                        is_video = True
                        pre_video_path = str(video_path)
                        print(f"[Media] {video_path} recognized as VALID video")
                    else:
                        # 壊れた動画 → 画像扱いにフォールバック
                        print(f"[Media] {video_path} exists but cannot read → fallback to image")
                        is_video = False
                        pre = None
                        pre_video_path = None
                    cap.release()
                except Exception as e:
                    print("[Media] video preload error:", e)
                    is_video = False
                    pre = None
                    pre_video_path = None

            # -----------------------------
            # 2) 静止画判定（png → jpg）
            # -----------------------------
            if not is_video:
                img_path = img_png if img_png.exists() else img_jpg if img_jpg.exists() else None
                if img_path:
                    try:
                        img = cv2.imread(str(img_path))
                        if img is not None:
                            pre = img.copy()
                            is_bgr = True
                            is_video = False
                            print(f"[Media] {img_path} loaded as image")
                        else:
                            print(f"[Media] image load failed: {img_path}")
                            pre = None
                            is_bgr = True
                            is_video = False
                    except Exception as e:
                        print("[Media] image preload error:", e)
                        pre = None
                        is_bgr = True
                        is_video = False
                else:
                    print(f"[Media] no media found for state {state}")

            # -----------------------------
            # プリロード結果を保存
            # -----------------------------
            with self._preload_lock:
                self._preloaded = pre
                self._preloaded_is_bgr = is_bgr
                self._preloaded_is_video = is_video
                self._preloaded_video_path = pre_video_path

        except Exception as e:
            print("[Media] _preload_state unexpected error:", e)
            with self._preload_lock:
                self._preloaded = None
                self._preloaded_is_bgr = True
                self._preloaded_is_video = False
                self._preloaded_video_path = None

    # ---------------------------------------------------------
    # public: メインスレッドでプリロード済みを適用
    # ---------------------------------------------------------
    def apply_preloaded_state(self):
        with self._preload_lock:
            if (
                self._preloaded is None
                and not self._preloaded_is_video
                and not self._preloaded_video_path
            ):
                return False

            # swap
            self._current_frame = self._preloaded
            self.frame_is_bgr = self._preloaded_is_bgr
            self.current_is_video = self._preloaded_is_video

            # 動画なら main-thread で VideoCapture を開く
            if self._preloaded_is_video and self._preloaded_video_path:
                try:
                    if getattr(self, "_video_cap", None) is not None:
                        try:
                            self._video_cap.release()
                        except:
                            pass
                        self._video_cap = None

                    self._video_cap = cv2.VideoCapture(self._preloaded_video_path)
                except Exception as e:
                    print("[Media] apply_preloaded_state video open error:", e)
                    self._video_cap = None

            # clear preload
            self._preloaded = None
            self._preloaded_is_bgr = True
            self._preloaded_is_video = False
            self._preloaded_video_path = None

            if self._current_frame is not None:
                self.last_frame_time = time.time()

            self._ended = False
            return True

    # ---------------------------------------------------------
    # public: 毎フレーム呼ばれる
    # ---------------------------------------------------------
    def get_frame(self):
        try:
            # 動画再生
            if getattr(self, "_video_cap", None) is not None and self._video_cap.isOpened():
                ret, frame = self._video_cap.read()
                if not ret:
                    # EOF
                    try:
                        self._video_cap.release()
                    except:
                        pass
                    self._video_cap = None
                    self._ended = True
                    return self._current_frame

                self._current_frame = frame
                self.frame_is_bgr = True
                self.last_frame_time = time.time()
                return frame

            # 静止画
            if self._current_frame is not None:
                self.last_frame_time = time.time()
                return self._current_frame

            return None

        except Exception as e:
            print("[Media] get_frame error:", e)
            return None

    # ---------------------------------------------------------
    def has_ended(self):
        return self._ended

    def clear_ended(self):
        self._ended = False
