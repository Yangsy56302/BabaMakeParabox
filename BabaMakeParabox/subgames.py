from BabaMakeParabox import displays, objects

import pygame

window_size = (192, 192)

def new_window(pipe, wps: float, obj: objects.Object) -> None:
    pygame.init()
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption(obj.sprite_name)
    displays.sprites.update()
    sprites = list(map(lambda i: displays.sprites.get(obj.sprite_name, obj.sprite_state, i), range(1, 4)))
    pygame.display.set_icon(sprites[0])
    clock = pygame.time.Clock()
    wiggle = 0
    game_running = True
    while game_running:
        try:
            if pipe.poll():
                if pipe.recv():
                    pygame.quit()
                    game_running = False
        except BrokenPipeError:
            game_running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
        window.fill("#000000")
        window.blit(pygame.transform.scale(sprites[wiggle], window_size), (0, 0))
        pygame.display.flip()
        wiggle = (wiggle + 1) % 3
        clock.tick(wps)
    pygame.quit()