# core/pet_manager.py

import json
import time
import pygame
from pathlib import Path
from utils.normalize import normalize_text


class PetManager:
    def __init__(self, json_path="data/pets_alias.json"):
        self.current_pet = ""
        self.last_switch_time = 0

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.load_aliases(json_path)

    def load_aliases(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.pet_aliases = {
                normalize_text(pet): [normalize_text(a) for a in aliases]
                for pet, aliases in raw.items()
            }
        except:
            self.pet_aliases = {}

    def set_current_pet(self, pet):
        pet = normalize_text(pet)
        print(f"[PetManager] set_current_pet: {pet}")
        self.current_pet = pet
        self.last_switch_time = time.time()

    def get_current_pet(self):
        return self.current_pet

    def get_bark_sound(self):
        pet = self.current_pet
        pet_bark = Path(f"assets/{pet}/bark.mp3")
        if pet_bark.exists():
            return str(pet_bark)

        common = Path("assets/bark.mp3")
        if common.exists():
            return str(common)

        return ""

    def play_bark(self):
        path = self.get_bark_sound()
        if not path:
            print("[Audio] bark が見つかりません")
            return
        try:
            sound = pygame.mixer.Sound(path)
            sound.play()
            print(f"[Audio] bark 再生: {path}")
        except Exception as e:
            print("[Audio] bark 再生失敗:", e)
