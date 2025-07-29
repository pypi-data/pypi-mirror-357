import numpy as np
import pathlib
from pylitematic import BlockPosition, BlockState, ResourceLocation, Schematic

path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/subs.litematic")
path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/creeper_test.litematic")
path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/regions.litematic")
stone = BlockState.from_string("minecraft:stone")
dirt = BlockState.from_string("minecraft:dirt")
s = Schematic.load(path)
print(f"{s.volume=} {s.size=} {s.bounds=}")
for name, reg in s.regions():
    print(name)
    print(f"\t{reg.shape=} {reg.volume=} {reg.block_count=}")
    print(f"\t{reg.origin=!s} {reg.limit=!s}")
    print(f"\t{reg.start=!s} {reg.end=!s}")
    print(f"\t{reg.lower=!s} {reg.upper=!s} {reg.size=}")
    # print(f"\t{reg[..., 1, 0]}")
    # print(f"\t{reg[:][1][0]}")
    # print(f"\t{reg[BlockPosition(0, 1, 0)]}")
    # reg[1,1,1] = BlockState.from_string("minecraft:stone")
    # print("lol: ", reg[reg.end])
    reg[0,:,0] = BlockState("minecraft:obsidian")
    reg[0,:,0] = [dirt, stone, dirt]
    # print(reg[...,0])
    # print(reg[np.array([BlockPosition(0, 0, 0), BlockPosition(1, 1, 1)])])
    # print(f"\t{reg[:]}")
    # for pos, state in reg.blocks(exclude_air=True):
    #     print(pos, state)
    # for pos, state in reg.blocks((BlockState("oak_log", axis="x"), BlockState("spruce_log", axis="z")), ignore_props=True):
    for pos, state in reg.blocks(exclude=BlockState("air")):
        print(pos, reg._to_internal(pos), state)
    for pos, state in reg.blocks(include=BlockState("air")):
        reg[pos] = BlockState("minecraft:netherrack")
    print(BlockState("oak_log", axis="x") in reg)
    print(BlockPosition(1, 1, 0) in reg)
    print(ResourceLocation("birch_log") in reg)
    # print(reg[0,:,2])
s.save("/mnt/d/minecraft/schematics/Litematica/test/aaa.litematic")
