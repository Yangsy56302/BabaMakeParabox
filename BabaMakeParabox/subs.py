from BabaMakeParabox import displays, objects

import pygame

def sub(json_name: str) -> None:
    pygame.init()
    window_size = (192, 192)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption(json_name)
    displays.sprites.update()
    sprites = list(map(lambda i: displays.sprites.get(objects.object_name[json_name].sprite_name, 0, i), range(1, 4)))
    pygame.display.set_icon(sprites[0])
    clock = pygame.time.Clock()
    wiggle = 0
    game_running = True
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
        window.fill("#000000")
        window.blit(pygame.transform.scale(sprites[wiggle], window_size), (0, 0))
        pygame.display.flip()
        wiggle = (wiggle + 1) % 3
        clock.tick(3)
    pygame.quit()