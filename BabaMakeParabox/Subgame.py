from BabaMakeParabox import Color, Object, Render

import pygame

def sub(json_name: str) -> None:
    pygame.init()
    window_size = (Render.sprite_size * 10, Render.sprite_size * 10)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption(Object.name_to_class[json_name].display_name)
    Color.set_palette("./palettes/variant.png")
    Render.current_sprites.update()
    sprites = list(map(lambda i: Render.current_sprites.get(json_name, 0, i), range(1, 4)))
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
        clock.tick(6)
    pygame.quit()