# engines/whisper_engine.py
#
# WhisperCPU を使って実際にマイク音声を認識するエンジン。
# - マイク入力
# - 無音判定
# - スレッドループ
# - pause/resume
# - callback 呼び出し
#
# WhisperCPU は「transcribe(audio_float32)」だけを提供するので、
# 音声入力とループはここで実装する。

import threading
import time
import numpy as np
import sounddevice as sd

from engines.whisper_cpu import WhisperCPU


class WhisperEngine:
    def __init__(self, samplerate=16000, block_size=1024):
        print("[Main] WhisperEngine 起動")

        self.cpu = WhisperCPU()  # 本物のモデル
        self.callback = None

        self.samplerate = samplerate
        self.block_size = block_size

        self._running = False
        self._paused = False
        self._listen_lock = threading.Lock()

        self._thread = None

    # -------------------------------------------------
    # 外部 API
    # -------------------------------------------------
    def set_callback(self, cb):
        self.callback = cb

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def pause_listen(self):
        with self._listen_lock:
            self._paused = True
            print("[Whisper] paused")

    def resume_listen(self):
        with self._listen_lock:
            self._paused = False
            print("[Whisper] resumed")

    # -------------------------------------------------
    # メインループ（マイク → WhisperCPU → callback）
    # -------------------------------------------------
    def _loop(self):
        print("[Whisper] 認識ループ開始")

        # sounddevice の入力ストリーム
        with sd.InputStream(
            channels=1,
            samplerate=self.samplerate,
            blocksize=self.block_size,
            dtype="float32"
        ) as stream:

            audio_buffer = []

            while self._running:
                # pause 中は待機
                with self._listen_lock:
                    if self._paused:
                        time.sleep(0.1)
                        continue

                # マイクから読み取り
                try:
                    data, _ = stream.read(self.block_size)
                except Exception as e:
                    print("[Whisper] audio read error:", e)
                    time.sleep(0.1)
                    continue

                # numpy.float32 の 1ch PCM
                audio_buffer.append(data[:, 0].copy())

                # 0.5秒分たまったら認識
                if len(audio_buffer) * self.block_size >= self.samplerate * 0.5:
                    chunk = np.concatenate(audio_buffer)
                    audio_buffer = []

                    # 無音判定（平均振幅が小さければ無視）
                    if np.abs(chunk).mean() < 0.005:
                        continue

                    # WhisperCPU で認識
                    try:
                        text = self.cpu.transcribe(chunk)
                    except Exception as e:
                        print("[Whisper] transcribe error:", e)
                        continue

                    if text and self.callback:
                        try:
                            self.callback(text, engine="whisper")
                        except Exception as e:
                            print("[Whisper] callback error:", e)

        print("[Whisper] 認識ループ終了")
