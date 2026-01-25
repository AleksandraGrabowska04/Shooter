import pygame

from camera import Camera
from settings import *
import random
from itertools import cycle

class Player(Camera):
    def __init__(self, eng, position=PLAYER_POS, yaw=0, pitch=0):
        self.app = eng.app
        self.eng = eng
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
        self.weapon_ids = list(self.weapons.keys())
        self.weapon_index = 0

        # gesture control
        self.gesture_active = False
        self.gesture_move = glm.vec2(0, 0)
        self.gesture_turn = 0.0
        self.gesture_shoot = False
        self.gesture_weapon_change = 0
        self.gesture_interact = False

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

    def handle_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == KEYS['INTERACT']:
                self.interact_with_door()

            # switch weapon by keys
            if event.key == KEYS['WEAPON_1']:
                self.switch_weapon(weapon_id=ID.KNIFE_0)
            elif event.key == KEYS['WEAPON_2']:
                self.switch_weapon(weapon_id=ID.PISTOL_0)
            if event.key == KEYS['WEAPON_3']:
                self.switch_weapon(weapon_id=ID.RIFLE_0)

        # switch weapon by mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            direction = 1 if event.y > 0 else -1
            self.cycle_weapon(direction)

        # shooting
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.do_shot()

    def check_health(self):
        if self.health <= 0:
            # self.play(self.sound.player_death)
            #
            pg.time.wait(2000)
            # self.eng.player_attribs = PlayerAttribs()
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
            self.weapon_index = self.weapon_ids.index(weapon_id)
            if hasattr(self, "weapon_instance") and self.weapon_instance:
                self.weapon_instance.weapon_id = self.weapon_id

    def cycle_weapon(self, direction: int) -> None:
        if direction == 0:
            return

        for _ in range(len(self.weapon_ids)):
            self.weapon_index = (self.weapon_index + (1 if direction > 0 else -1)) % len(self.weapon_ids)
            weapon_id = self.weapon_ids[self.weapon_index]
            if self.weapons[weapon_id]:
                self.switch_weapon(weapon_id=weapon_id)
                break

    def do_shot(self):
        if self.weapon_id == ID.KNIFE_0:
            self.is_shot = True
            self.check_hit_on_npc()
            #
            # self.play(self.sound.player_attack[ID.KNIFE_0])

        elif self.ammo:
            consumption = WEAPON_SETTINGS[self.weapon_id]['ammo_consumption']
            if not self.is_shot and self.ammo >= consumption:
                self.is_shot = True
                self.check_hit_on_npc()
                #
                self.ammo -= consumption
                self.ammo = max(0, self.ammo)
                #
                # self.play(self.sound.player_attack[self.weapon_id])

    def interact_with_door(self):
        pos = self.position + self.forward
        int_pos = int(pos.x), int(pos.z)

        if int_pos in self.door_map:
            door = self.door_map[int_pos]
            door.is_moving = True

    def update(self):
        if self.gesture_active:
            self._apply_gesture_control()
        else:
            self.mouse_control()
            self.keyboard_control()
        # self.position.x += 0.1
        # print(str(self.position) + "####"+ str(self.yaw))         # TODO: checkpoint
        super().update()


        self.update_tile_position()
        self.pick_up_item()

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        vel = PLAYER_SPEED * self.app.delta_time
        next_step = glm.vec2()
        #
        if key_state[KEYS['FORWARD']]:
            next_step += self.move_forward(vel)
        if key_state[KEYS['BACK']]:
            next_step += self.move_back(vel)
            # next_step += self.move_up(vel)
        if key_state[KEYS['STRAFE_R']]:
            next_step += self.move_right(vel)
        if key_state[KEYS['STRAFE_L']]:
            next_step += self.move_left(vel)
        # if key_state[KEYS['UP']]:
        #     next_step += self.move_up(vel)
        # if key_state[KEYS['DOWN']]:
        #     next_step += self.move_down(vel)
        #
        self.move(next_step=next_step)

    def set_gesture_input(
        self,
        active: bool,
        move=(0.0, 0.0),
        turn: float = 0.0,
        shoot: bool = False,
        weapon_change: int = 0,
        interact: bool = False,
    ) -> None:
        self.gesture_active = active
        self.gesture_move = glm.vec2(move[0], move[1])
        self.gesture_turn = turn
        self.gesture_shoot = shoot
        self.gesture_weapon_change = weapon_change
        self.gesture_interact = interact

    def _apply_gesture_control(self) -> None:
        vel = PLAYER_SPEED * self.app.delta_time
        next_step = glm.vec2()

        if self.gesture_move.y < 0:
            next_step += self.move_forward(vel * abs(self.gesture_move.y))
        elif self.gesture_move.y > 0:
            next_step += self.move_back(vel * abs(self.gesture_move.y))

        if self.gesture_move.x > 0:
            next_step += self.move_right(vel * abs(self.gesture_move.x))
        elif self.gesture_move.x < 0:
            next_step += self.move_left(vel * abs(self.gesture_move.x))

        if next_step.x or next_step.y:
            self.move(next_step=next_step)

        if self.gesture_turn:
            self.rotate_yaw(delta_x=self.gesture_turn * PLAYER_ROT_SPEED * self.app.delta_time)

        if self.gesture_weapon_change:
            self.cycle_weapon(self.gesture_weapon_change)

        if self.gesture_shoot:
            self.do_shot()
        if self.gesture_interact:
            self.interact_with_door()

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
