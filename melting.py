from PIL import Image
from argparse import ArgumentParser
from pathlib import Path
from math import ceil
from random import randint

rndtable = [
    0,   8, 109, 220, 222, 241, 149, 107,  75, 248, 254, 140,  16,  66 ,
    74,  21, 211,  47,  80, 242, 154,  27, 205, 128, 161,  89,  77,  36 ,
    95, 110,  85,  48, 212, 140, 211, 249,  22,  79, 200,  50,  28, 188 ,
    52, 140, 202, 120,  68, 145,  62,  70, 184, 190,  91, 197, 152, 224 ,
    149, 104,  25, 178, 252, 182, 202, 182, 141, 197,   4,  81, 181, 242 ,
    145,  42,  39, 227, 156, 198, 225, 193, 219,  93, 122, 175, 249,   0 ,
    175, 143,  70, 239,  46, 246, 163,  53, 163, 109, 168, 135,   2, 235 ,
    25,  92,  20, 145, 138,  77,  69, 166,  78, 176, 173, 212, 166, 113 ,
    94, 161,  41,  50, 239,  49, 111, 164,  70,  60,   2,  37, 171,  75 ,
    136, 156,  11,  56,  42, 146, 138, 229,  73, 146,  77,  61,  98, 196 ,
    135, 106,  63, 197, 195,  86,  96, 203, 113, 101, 170, 247, 181, 113 ,
    80, 250, 108,   7, 255, 237, 129, 226,  79, 107, 112, 166, 103, 241 ,
    24, 223, 239, 120, 198,  58,  60,  82, 128,   3, 184,  66, 143, 224 ,
    145, 224,  81, 206, 163,  45,  63,  90, 168, 114,  59,  33, 159,  95 ,
    28, 139, 123,  98, 125, 196,  15,  70, 194, 253,  54,  14, 109, 226 ,
    71,  17, 161,  93, 186,  87, 244, 138,  20,  52, 123, 251,  26,  36 ,
    17,  46,  52, 231, 232,  76,  31, 221,  84,  37, 216, 165, 212, 106 ,
    197, 242,  98,  43,  39, 175, 254, 145, 190,  84, 118, 222, 187, 136 ,
    120, 163, 236, 249
]

rndindex = 0x0

def M_Random():
    global rndindex
    rndindex = (rndindex + 1) & 0xff
    return rndtable[rndindex]

def doom_randint(min, max):
    return min + M_Random() % (max - min + 1)

parser = ArgumentParser()

parser.add_argument('background', type=Path, help="Image that should be used as the background")
parser.add_argument('foreground', type=Path, help="Image that should be used as the foreground")

parser.add_argument('--column-size', type=int, default=2)
parser.add_argument('--max-offset', type=int, default=15)
parser.add_argument('--step-size', type=int, default=8)

parser.add_argument('--doom-rnd', dest="random", action="store_const", const=doom_randint, default=randint, help="Use original Doom random numbere generation")

args = parser.parse_args()

background = Image.open(args.background)
foreground = Image.open(args.foreground)

assert background.size == foreground.size, "Images are different sizes"
assert background.mode == foreground.mode, "Images are different modes"

column_offsets = [None] * ceil(background.size[0] / args.column_size)
column_offsets[0] = args.random(0, args.max_offset)
for i in range(1, len(column_offsets)):
    column_offsets[i] = column_offsets[i - 1] + -args.random(-1, 1)
    if column_offsets[i] < 0:
        column_offsets[i] = 0
    elif column_offsets[i] > args.max_offset:
        column_offsets[i] = args.max_offset

columns = [None] * ceil(background.size[0] / args.column_size)
for i in range(len(columns)):
    copy = foreground.copy()
    columns[i] = copy.crop((i * args.column_size, 0, (i + 1) * args.column_size, background.size[1]))

frames = []

for i in range(ceil(background.size[1] / args.step_size) + args.max_offset + 1):
    buffer = background.copy()
    for j in range(len(column_offsets)):
        if column_offsets[j] >= 0:
            buffer.paste(columns[j], (j * args.column_size, 0))
        else:
            buffer.paste(columns[j], (j * args.column_size, -column_offsets[j] * args.step_size))
        column_offsets[j] -= 1
    
    frames.append(buffer)

gif = frames[0].copy()
gif.save("out.gif", save_all=True, append_images=frames[1:])