import cv2
import time
import os

class CameraDetector:
    def __init__(self, debug=False):
        self.debug = debug

        # カメラ初期化
        self.cap = cv2.VideoCapture(0)

        # 過敏反応防止のクールダウン
        self.last_event_time = 0
        self.COOLDOWN = 2.0  # 2秒

        # ---------------------------------------------------------
        # HaarCascade のパス
        # ---------------------------------------------------------
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, ".."))
        cascade_dir = os.path.join(project_root, "data")

        face_xml = os.path.join(cascade_dir, "haarcascade_frontalface_default.xml")
        smile_xml = os.path.join(cascade_dir, "haarcascade_smile.xml")

        self.face_cascade = cv2.CascadeClassifier(face_xml)
        self.smile_cascade = cv2.CascadeClassifier(smile_xml)

        if self.face_cascade.empty():
            print("[Camera] face_cascade の読み込みに失敗:", face_xml)

        if self.smile_cascade.empty():
            print("[Camera] smile_cascade の読み込みに失敗:", smile_xml)

    # ---------------------------------------------------------
    # カメラ検出
    # ---------------------------------------------------------
    def detect(self):
        now = time.time()

        # クールダウン中は検出しない
        if now - self.last_event_time < self.COOLDOWN:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 顔検出（パラメータ緩め）
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]

            # ★ 笑顔検出（大幅に緩める）
            smiles = self.smile_cascade.detectMultiScale(
                roi,
                scaleFactor=1.2,
                minNeighbors=8,
                minSize=(30, 30)
            )

            if len(smiles) > 0:
                print("[Camera] 笑顔検出")
                self.last_event_time = now
                return "smile"

        return None
