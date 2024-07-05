import baba_make_parabox.objects as objects
import baba_make_parabox.levels as levels
import baba_make_parabox.worlds as worlds

import pygame

window = pygame.display.set_mode((1080, 720))
clock = pygame.time.Clock()
game_running = True

keybinds = {"W": pygame.K_w,
            "A": pygame.K_a,
            "S": pygame.K_s,
            "D": pygame.K_d,
            "Z": pygame.K_z,
            "R": pygame.K_r,
            "_": pygame.K_SPACE}

cooldowns = {value: 0 for value in keybinds.values()}
default_cooldown = 3

level_0 = levels.level("0", 0, (9, 9))
level_0.new_obj(objects.Baba((3, 3), "W"))

level_0.new_obj(objects.Wall((1, 4), "W"))
level_0.new_obj(objects.Wall((4, 1), "W"))

level_0.new_obj(objects.Level((3, 5), "W", name="0", inf_tier=0))
level_0.new_obj(objects.Clone((5, 5), "W", name="0", inf_tier=0))

level_0_pos_1 = levels.level("0", 1, (3, 3))

level_0_neg_1 = levels.level("0", -1, (3, 3))

level_v = levels.level("test", -1, (9, 9))

level_v.new_obj(objects.Level((2, 2), "W", name="0", inf_tier=-1))
level_v.new_obj(objects.Level((4, 2), "W", name="0", inf_tier=0))
level_v.new_obj(objects.Level((6, 2), "W", name="0", inf_tier=1))

world = worlds.world(level_0, level_0_pos_1, level_0_neg_1, level_v,
                     rule_list=[(objects.BABA, objects.IS, objects.YOU),
                                (objects.TEXT, objects.IS, objects.PUSH),
                                (objects.LEVEL, objects.IS, objects.PUSH),
                                (objects.CLONE, objects.IS, objects.PUSH),
                                (objects.WALL, objects.IS, objects.STOP)])

window.fill("#444444")
for i, level in enumerate(world.level_list):
    window.blit(pygame.transform.scale(world.show_level(level, 2), (360, 360)), (360 * (i % 3), 360 * (i // 3)))
pygame.display.flip()
while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
    keys = pygame.key.get_pressed()
    refresh = False
    if keys[keybinds["W"]] and cooldowns[keybinds["W"]] == 0:
        world.round("W")
        cooldowns[keybinds["W"]] = default_cooldown
        refresh = True
    elif keys[keybinds["S"]] and cooldowns[keybinds["S"]] == 0:
        world.round("S")
        cooldowns[keybinds["S"]] = default_cooldown
        refresh = True
    elif keys[keybinds["A"]] and cooldowns[keybinds["A"]] == 0:
        world.round("A")
        cooldowns[keybinds["A"]] = default_cooldown
        refresh = True
    elif keys[keybinds["D"]] and cooldowns[keybinds["D"]] == 0:
        world.round("D")
        cooldowns[keybinds["D"]] = default_cooldown
        refresh = True
    if refresh:
        window.fill("#444444")
        for i, level in enumerate(world.level_list):
            window.blit(pygame.transform.scale(world.show_level(level, 2), (360, 360)), (360 * (i % 3), 360 * (i // 3)))
        pygame.display.flip()
    for key in cooldowns:
        if cooldowns[key] > 0:
            cooldowns[key] -= 1
    clock.tick(15)

pygame.quit()