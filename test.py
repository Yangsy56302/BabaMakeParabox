import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

surface = pygame.Surface((640, 360), pygame.SRCALPHA)
surface.fill("#FFFFFF88")
surface.fill("#88888888", special_flags=pygame.BLEND_MULT)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill("#8800FF")
    screen.blit(surface, (320, 180))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()