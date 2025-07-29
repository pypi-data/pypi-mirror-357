import pathlib
from pylitematic import BlockPosition, BlockState, Schematic


path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/subs.litematic")
path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/creeper_test.litematic")
path = pathlib.Path("/mnt/d/minecraft/schematics/Litematica/test/regions.litematic")
stone = BlockState.from_string("minecraft:stone")
dirt = BlockState.from_string("minecraft:dirt")
s = Schematic.load(path)
print(f"{s.volume=} {s.size=} {s.bounds=}")
for name, reg in s.regions():
    print(name)
    print(f"\t{reg.shape=} {reg.volume=} {reg.blocks=}")
    print(f"\t{reg.origin=!s} {reg.end=!s}")
    print(f"\t{reg.lower=} {reg.upper=!s} {reg.size=}")
    # print(f"\t{reg[..., 1, 0]}")
    # print(f"\t{reg[:][1][0]}")
    # print(f"\t{reg[BlockPosition(0, 1, 0)]}")
    reg[1,1,1] = BlockState.from_string("minecraft:stone")
    reg[0,:,0] = [dirt, stone, dirt]
    print(f"\t{reg[:]}")
s.save("/mnt/d/minecraft/schematics/Litematica/test/pylitematic.litematic")
