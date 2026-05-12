# core/app.py

import pygame
import time


def start_desktop_pet(initial_pet, pet_manager, state_manager, media_manager):
    pet_manager.set_current_pet(initial_pet)
    state_manager.change_state("n1")

    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 状態更新
        state_manager.update()

        # 画面クリア
        screen.fill((0, 0, 0))

        # フレーム取得
        frame = media_manager.get_frame()
        if frame is not None:
            # frame: (H, W, 3) の想定
            h, w, _ = frame.shape
            surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            sw, sh = screen.get_size()
            scale = min(sw / w, sh / h)
            new_w = int(w * scale)
            new_h = int(h * scale)

            surf = pygame.transform.smoothscale(surf, (new_w, new_h))

            x = (sw - new_w) // 2
            y = (sh - new_h) // 2
            screen.blit(surf, (x, y))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


