from PIL import Image
from argparse import ArgumentParser
from pathlib import Path
from math import ceil
from random import randint

parser = ArgumentParser()

parser.add_argument('background', type=Path, help="Image that should be used as the background")
parser.add_argument('foreground', type=Path, help="Image that should be used as the foreground")

parser.add_argument('--column-size', type=int, default=2)
parser.add_argument('--max-offset', type=int, default=15)
parser.add_argument('--step-size', type=int, default=8)

args = parser.parse_args()

background = Image.open(args.background)
foreground = Image.open(args.foreground)

assert background.size == foreground.size, "Images are different sizes"
assert background.mode == foreground.mode, "Images are different modes"

column_offsets = [None] * ceil(background.size[0] / args.column_size)
column_offsets[0] = randint(0, args.max_offset)
for i in range(1, len(column_offsets)):
    column_offsets[i] = column_offsets[i - 1] + randint(-1, 1)
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