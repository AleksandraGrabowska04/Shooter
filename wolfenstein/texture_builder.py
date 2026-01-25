import math
import pathlib
import re
import pygame as pg
from settings import TEX_SIZE

BASE_DIR = pathlib.Path(__file__).resolve().parent

# cały ten plik odpowiada po prostu za pocięcie texturearray na teksturki
class TextureArrayBuilder:
    def __init__(self, should_build=True):
        if should_build:
            # main textures
            load_path = BASE_DIR / 'assets' / 'textures'
            texture_array_path = BASE_DIR / 'assets' / 'texture_array' / 'texture_array.png'
            sprite_sheet_path = BASE_DIR / 'assets' / 'sprite_sheet' / 'sprite_sheet.png'
            if not texture_array_path.exists() or not sprite_sheet_path.exists():
                self.build(
                    load_path=load_path,
                    texture_array_path=texture_array_path,
                    sprite_sheet_path=sprite_sheet_path
                )

    def build(self, load_path, texture_array_path, sprite_sheet_path, tex_size=TEX_SIZE):
        load_path = pathlib.Path(load_path)
        texture_array_path = pathlib.Path(texture_array_path)
        sprite_sheet_path = pathlib.Path(sprite_sheet_path)

        texture_paths = [item for item in load_path.rglob('*.png') if item.is_file()]
        texture_paths = sorted(
            texture_paths,
            key=lambda tex_path: int(re.search('\\d+', tex_path.stem).group(0))
        )
        # empty tex array
        texture_array = pg.Surface([tex_size, tex_size * len(texture_paths)], pg.SRCALPHA, 32)

        # empty sprite_sheet
        size = int(math.sqrt(len(texture_paths))) + 1
        sheet_size = tex_size * size
        sprite_sheet = pg.Surface([sheet_size, sheet_size], pg.SRCALPHA, 32)

        for i, path in enumerate(texture_paths):
            texture = pg.image.load(path)
            texture_array.blit(texture, (0, i * tex_size))
            sprite_sheet.blit(texture, ((i % size) * tex_size, (i // size) * tex_size))

        sprite_sheet_path.parent.mkdir(parents=True, exist_ok=True)
        texture_array_path.parent.mkdir(parents=True, exist_ok=True)
        pg.image.save(sprite_sheet, sprite_sheet_path)
        pg.image.save(texture_array, texture_array_path)
