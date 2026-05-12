# engines/camera_engine.py

import cv2
import threading
import time
import traceback

class CameraEngine:
    def __init__(self, callback=None, debug=True):
        self.callback = callback
        self.debug = debug
        self._running = False

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )

    def start(self):
        if self._running:
            return
        self._running = True

        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        try:
            # ★ バックエンドを明示（あなたの環境では DSHOW が安定）
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            if not cap.isOpened():
                print("[Camera] カメラが開けません")
                return

            print("[Camera] 起動完了")

            while self._running:
                ret, frame = cap.read()
                if not ret:
                    print("[Camera] フレーム取得失敗")
                    time.sleep(0.1)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    roi = gray[y:y+h, x:x+w]
                    smiles = self.smile_cascade.detectMultiScale(
                        roi,
                        scaleFactor=1.3,
                        minNeighbors=15
                    )

                    if len(smiles) > 0:
                        print("[Camera] smile detected")
                        if self.callback:
                            self.callback("smile")
                        time.sleep(2)

                time.sleep(0.1)

            cap.release()

        except Exception as e:
            print("[Camera] 例外発生:", e)
            traceback.print_exc()
