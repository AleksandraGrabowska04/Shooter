import os
from PIL import Image

# ------------ CONFIG -------------
INPUT_IMAGE = "canvas2.png"
OUTPUT_DIR = "textures"

ROWS = 3
COLS = 4
OUT_SIZE = 256
# ---------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

img = Image.open(INPUT_IMAGE).convert("RGBA")
sheet_w, sheet_h = img.size

cell_w = sheet_w / COLS
cell_h = sheet_h / ROWS

index = 0

for row in range(ROWS):
    for col in range(COLS):
        left   = int(col * cell_w)
        upper  = int(row * cell_h)
        right  = int((col + 1) * cell_w)
        lower  = int((row + 1) * cell_h)

        sprite = img.crop((left, upper, right, lower))
        sprite = sprite.resize((OUT_SIZE, OUT_SIZE), Image.NEAREST)

        out_path = os.path.join(OUTPUT_DIR, f"texture_{index:02}.png")
        sprite.save(out_path)
        index += 1

print(f"Saved {index} textures at {OUT_SIZE}x{OUT_SIZE}")
