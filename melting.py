from PIL import Image
from math import ceil
from random import randint

background = Image.open("background.png")
foreground = Image.open("foreground.png")

assert background.size == foreground.size, "Images are different sizes"
assert background.mode == foreground.mode, "Images are different modes"

column_size = 2
max_offset = 15
step_size = 8

column_offsets = [None] * ceil(background.size[0] / column_size)
column_offsets[0] = randint(0, max_offset)
for i in range(1, len(column_offsets)):
    if column_offsets[i] == None:
        column_offsets[i] = column_offsets[i - 1] + randint(-1, 1)
        if column_offsets[i] < 0:
            column_offsets[i] = 0
        elif column_offsets[i] > max_offset:
            column_offsets[i] = max_offset

columns = [None] * ceil(background.size[0] / column_size)
for i in range(len(columns)):
    copy = foreground.copy()
    columns[i] = copy.crop((i * column_size, 0, (i + 1) * column_size, background.size[1]))

frames = []

for i in range(ceil(background.size[1] / step_size) + max_offset + 1):
    buffer = background.copy()
    for j in range(len(column_offsets)):
        if column_offsets[j] >= 0:
            buffer.paste(columns[j], (j * column_size, 0))
        else:
            buffer.paste(columns[j], (j * column_size, -column_offsets[j] * step_size))
        column_offsets[j] -= 1
    
    frames.append(buffer)

gif = frames[0].copy()
gif.save("out.gif", save_all=True, append_images=frames[1:])