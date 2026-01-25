import pygame  # możesz to potem wywalić całkiem, jak nic już nie będzie używać pg
from camera import Camera
from settings import *
import random
from itertools import cycle


class Player(Camera):
    def __init__(self, eng, position=PLAYER_POS, yaw=0, pitch=0):
        self.app = eng.app
        self.eng = eng
        self.input = eng.input  # <<< JEDYNE źródło inputu
        super().__init__(position, yaw, pitch)

        # these maps will update when instantiated LevelMap
        self.door_map, self.wall_map, self.item_map = None, None, None

        # attribs
        self.health = PLAYER_INIT_HEALTH
        self.ammo = PLAYER_INIT_AMMO

        self.tile_pos = None, None

        self.is_shot = False

        # weapon
        self.weapons = {ID.KNIFE_0: 1, ID.PISTOL_0: 0, ID.RIFLE_0: 0}
        self.weapons_cycle = cycle(self.weapons.keys())
        self.weapon_id = ID.KNIFE_0

    def update_tile_position(self):
        self.tile_pos = int(self.position.x), int(self.position.z)

    def pick_up_item(self):
        if self.tile_pos not in self.item_map:
            return None

        item = self.item_map[self.tile_pos]

        if item.tex_id == ID.MED_KIT:
            self.health += ITEM_SETTINGS[ID.MED_KIT]['value']
            self.health = min(self.health, MAX_HEALTH_VALUE)

        elif item.tex_id == ID.AMMO:
            self.ammo += ITEM_SETTINGS[ID.AMMO]['value']
            self.ammo = min(self.ammo, MAX_AMMO_VALUE)

        elif item.tex_id == ID.PISTOL_ICON:
            if not self.weapons[ID.PISTOL_0]:
                self.weapons[ID.PISTOL_0] = 1
                self.switch_weapon(weapon_id=ID.PISTOL_0)

        elif item.tex_id == ID.RIFLE_ICON:
            if not self.weapons[ID.RIFLE_0]:
                self.weapons[ID.RIFLE_0] = 1
                self.switch_weapon(weapon_id=ID.RIFLE_0)

        del self.item_map[self.tile_pos]

    # <<< CAŁY INPUT JEST TU
    def handle_input(self):
        # interakcja
        if self.input.key_down('INTERACT'):
            self.interact_with_door()

        # zmiana broni klawiszami
        if self.input.key_down('WEAPON_1'):
            self.switch_weapon(weapon_id=ID.KNIFE_0)
        elif self.input.key_down('WEAPON_2'):
            self.switch_weapon(weapon_id=ID.PISTOL_0)
        elif self.input.key_down('WEAPON_3'):
            self.switch_weapon(weapon_id=ID.RIFLE_0)

        # zmiana broni rolką myszy
        if self.input.mouse_wheel:
            weapon_id = next(self.weapons_cycle)
            if self.weapons[weapon_id]:
                self.switch_weapon(weapon_id=weapon_id)

        # strzał
        if self.input.mouse_left_pressed():
            self.do_shot()

        # mysz – obrót kamery
        if self.input.mouse_dx:
            self.rotate_yaw(delta_x=self.input.mouse_dx * MOUSE_SENSITIVITY)
        if self.input.mouse_dy:
            self.rotate_pitch(delta_y=self.input.mouse_dy * MOUSE_SENSITIVITY)

        # klawiatura – ruch
        vel = PLAYER_SPEED * self.app.delta_time
        next_step = glm.vec2()

        if self.input.key_down('FORWARD'):
            next_step += self.move_forward(vel)
        if self.input.key_down('BACK'):
            next_step += self.move_back(vel)
        if self.input.key_down('STRAFE_R'):
            next_step += self.move_right(vel)
        if self.input.key_down('STRAFE_L'):
            next_step += self.move_left(vel)

        self.move(next_step=next_step)

    def check_health(self):
        if self.health <= 0:
            pygame.time.wait(2000)
            self.eng.new_game()

    def check_hit_on_npc(self):
        if WEAPON_SETTINGS[self.weapon_id]['miss_probability'] > random.random():
            return None

        if npc_pos := self.eng.ray_casting.run(
                start_pos=self.position,
                direction=self.forward,
                max_dist=WEAPON_SETTINGS[self.weapon_id]['max_dist'],
                npc_to_player_flag=False
        ):
            npc = self.eng.level_map.npc_map[npc_pos]
            npc.get_damage()

    def switch_weapon(self, weapon_id):
        if self.weapons[weapon_id]:
            self.weapon_id = weapon_id
            self.weapon_instance.weapon_id = self.weapon_id

    def do_shot(self):
        if self.weapon_id == ID.KNIFE_0:
            self.is_shot = True
            self.check_hit_on_npc()

        elif self.ammo:
            consumption = WEAPON_SETTINGS[self.weapon_id]['ammo_consumption']
            if not self.is_shot and self.ammo >= consumption:
                self.is_shot = True
                self.check_hit_on_npc()
                self.ammo -= consumption
                self.ammo = max(0, self.ammo)

    def interact_with_door(self):
        pos = self.position + self.forward
        int_pos = int(pos.x), int(pos.z)

        if int_pos in self.door_map:
            door = self.door_map[int_pos]
            door.is_moving = True

    def update(self):
        self.handle_input()
        super().update()
        self.update_tile_position()
        self.pick_up_item()

    def move(self, next_step):
        if not self.is_collide(dx=next_step[0]):
            self.position.x += next_step[0]

        if not self.is_collide(dz=next_step[1]):
            self.position.z += next_step[1]

    def is_collide(self, dx=0, dz=0):
        int_pos = (
            int(self.position.x + dx + (
                PLAYER_SIZE if dx > 0 else -PLAYER_SIZE if dx < 0 else 0)
                ),
            int(self.position.z + dz + (
                PLAYER_SIZE if dz > 0 else -PLAYER_SIZE if dz < 0 else 0)
                )
        )
        # check doors
        if int_pos in self.door_map:
            return self.door_map[int_pos].is_closed

        # check walls
        return int_pos in self.wall_map
