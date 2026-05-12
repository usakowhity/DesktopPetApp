import sys
import os

def resource_path(relative_path: str) -> str:
    """
    PyInstaller 6.x 対応版。
    exe 実行時は _MEIPASS/_internal を優先し、
    開発環境ではカレントディレクトリ基準の相対パスを返す。
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS

        # 6.x で datas が入る場所
        internal_path = os.path.join(base_path, "_internal", relative_path)
        if os.path.exists(internal_path):
            return internal_path

        # 旧来の配置（保険）
        legacy_path = os.path.join(base_path, relative_path)
        if os.path.exists(legacy_path):
            return legacy_path

    # 開発環境（VENV）用
    return os.path.join(os.path.abspath("."), relative_path)

