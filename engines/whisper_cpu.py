import whisper
import numpy as np

class WhisperCPU:
    def __init__(self, model_size="tiny"):
        print(f"[WhisperCPU] モデルをロード中... ({model_size})")
        self.model = whisper.load_model(model_size)
        print("[WhisperCPU] Whisper CPU版 初期化完了")

    def transcribe(self, audio_float32):
        """
        audio_float32: numpy.float32 の 1ch PCM（-1.0〜1.0）
        """
        if audio_float32 is None or len(audio_float32) == 0:
            return ""

        result = self.model.transcribe(
            audio_float32,
            language="ja",
            fp16=False,
            temperature=0.2,              # ← 精度向上
            beam_size=1,
            best_of=1,
            no_speech_threshold=0.5,
            condition_on_previous_text=False
        )

        return result["text"].strip()