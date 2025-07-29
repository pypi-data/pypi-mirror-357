import numpy as np
import pathlib
from pylitematic import BlockPosition, BlockId, BlockState, Region, Schematic, Size3D

# path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/subs.litematic")
# path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/regions.litematic")
# path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/creeper_test.litematic")
# stone = BlockState.from_string("minecraft:stone")
# dirt = BlockState.from_string("minecraft:dirt")
# s = Schematic.load(path)
# print(f"{s.volume=} {s.size=} {s.bounds=}")
# for name, reg in s.regions():
#     print(name)
#     print(f"\t{reg.shape=} {reg.volume=} {reg.block_count=}")
#     print(f"\t{reg.origin=!s} {reg.limit=!s}")
#     print(f"\t{reg.start=!s} {reg.end=!s}")
#     print(f"\t{reg.lower=!s} {reg.upper=!s} {reg.size=}")
#     # print(f"\t{reg[..., 1, 0]}")
#     # print(f"\t{reg[:][1][0]}")
#     # print(f"\t{reg[BlockPosition(0, 1, 0)]}")
#     # reg[1,1,1] = BlockState.from_string("minecraft:stone")
#     # print("lol: ", reg[reg.end])
#     # reg[0,:,0] = BlockState("minecraft:obsidian")
#     # reg[0,:,0] = [dirt, stone, dirt]
#     # print(reg[...,0])
#     # print(reg[np.array([BlockPosition(0, 0, 0), BlockPosition(1, 1, 1)])])
#     # print(f"\t{reg[:]}")
#     # for pos, state in reg.blocks(exclude_air=True):
#     #     print(pos, state)
#     # for pos, state in reg.blocks((BlockState("oak_log", axis="x"), BlockState("spruce_log", axis="z")), ignore_props=True):
#     # reg[...,-1] = stone
#     for pos, state in reg.blocks(exclude=BlockState("air")):
#         print(f"\t{pos} {reg._to_internal(pos)}: {state}")
#     for pos, state in reg.blocks(include=BlockState("lime_wool")):
#         reg[pos] = BlockState("minecraft:blue_wool")
#     for pos, state in reg.blocks(include=BlockState("tripwire"), ignore_props=True):
#         reg[pos] = BlockState("minecraft:glass")
#     # print(BlockState("oak_log", axis="x") in reg)
#     # print(BlockPosition(1, 1, 0) in reg)
#     # print(ResourceLocation("birch_log") in reg)
#     # print(reg[0,:,2])
# s.save("/mnt/d/minecraft/schematics/Litematica/test/aaa.litematic")

air = BlockState("air")
stone = BlockState("stone")
dirt = BlockState("dirt")
grass = BlockState("grass_block")
cobble = BlockState("mossy_cobblestone")
snow = BlockState("snow_block")
pumpkin = BlockState("carved_pumpkin", facing="west")

ground = Region(size=Size3D(16, 9, 16), origin=BlockPosition(0, 0, 0))
ground[:,:5,:] = stone
ground[:,5:8,:] = dirt
ground[:,8:,:] = grass

boulder = Region(size=(4, 4, 4), origin=ground.origin+[6, ground.height, 6])
boulder[:] = cobble

# snow_man = Region(size=(1, 3, 1), origin=boulder.origin+[1, boulder.height, 1])
snow_man = Region(size=(-1, -3, -1), origin=boulder.origin+[1, boulder.height+2, 1])
snow_man[:] = snow
snow_man[0,snow_man.upper.y,0] = pumpkin

schem = Schematic(name="scene", author="Boscawinks", description="A simple scene")
schem.add_region("ground", ground)
schem.add_region("boulder", boulder)
schem.add_region("snow_man", snow_man)
schem.save(f"/mnt/d/minecraft/schematics/Litematica/test/{schem.name}.litematic")

print(snow_man == snow)