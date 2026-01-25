import glm
from settings import MAX_RAY_DIST


class RayCasting:
    def __init__(self, eng):
        self.eng = eng
        self.level_map = eng.level_map
        self.wall_map = eng.level_map.wall_map
        self.door_map = eng.level_map.door_map
        self.player = eng.player

    @staticmethod
    def _init_dda(pos, ray_dir):
        """
        Klasyczna inicjalizacja DDA (Wolf3D)
        """
        map_x = int(glm.floor(pos.x))
        map_y = int(glm.floor(pos.y))

        if ray_dir.x == 0.0:
            delta_x = 1e30
            step_x = 0
            side_x = 1e30
        else:
            delta_x = abs(1.0 / ray_dir.x)
            step_x = 1 if ray_dir.x > 0 else -1
            side_x = (
                (map_x + 1.0 - pos.x) if step_x > 0 else (pos.x - map_x)
            ) * delta_x

        if ray_dir.y == 0.0:
            delta_y = 1e30
            step_y = 0
            side_y = 1e30
        else:
            delta_y = abs(1.0 / ray_dir.y)
            step_y = 1 if ray_dir.y > 0 else -1
            side_y = (
                (map_y + 1.0 - pos.y) if step_y > 0 else (pos.y - map_y)
            ) * delta_y

        return map_x, map_y, step_x, step_y, side_x, side_y, delta_x, delta_y

    def run(self, start_pos, direction, max_dist=MAX_RAY_DIST, npc_to_player_flag=True):
        """
        2D raycasting (X,Z → map X,Y)
        """
        # pozycja w 2D
        pos = glm.vec2(start_pos.x, start_pos.z)

        # kierunek (musi być znormalizowany!)
        ray_dir = glm.normalize(glm.vec2(direction.x, direction.z))

        map_x, map_y, step_x, step_y, side_x, side_y, delta_x, delta_y = \
            self._init_dda(pos, ray_dir)

        max_steps = int(max_dist * 2)

        for _ in range(max_steps):
            tile_pos = (map_x, map_y)

            # ------------------ kolizje ------------------
            if tile_pos in self.wall_map:
                return False

            if tile_pos in self.door_map:
                if self.door_map[tile_pos].is_closed:
                    return False

            # NPC → gracz
            if npc_to_player_flag:
                if self.player.tile_pos == tile_pos:
                    return True
            # gracz → NPC
            else:
                if tile_pos in self.level_map.npc_map:
                    return tile_pos
            # ---------------------------------------------

            # krok DDA
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
            else:
                side_y += delta_y
                map_y += step_y

        return False
