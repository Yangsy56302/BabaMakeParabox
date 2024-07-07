from baba_make_parabox import *

level = levels.level("only", (5, 5))
level.new_obj(objects.BABA((1, 1)))
level.new_obj(objects.IS((1, 2)))
level.new_obj(objects.YOU((1, 3)))
level.new_obj(objects.FLAG((3, 1)))
level.new_obj(objects.IS((3, 2)))
level.new_obj(objects.YOU((3, 3)))
level.new_obj(objects.WIN((3, 3)))
level.new_obj(objects.IS((2, 2)))
level.new_obj(objects.Baba((2, 1)))

world = worlds.world("transform", [level])

play(world)
stop()