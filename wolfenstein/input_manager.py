import pygame as pg

class InputManager:
    def __init__(self):
        self.keys_map = {
            'FORWARD': pg.K_w,
            'BACK': pg.K_s,
            'STRAFE_L': pg.K_a,
            'STRAFE_R': pg.K_d,
            'INTERACT': pg.K_e,
            'WEAPON_1': pg.K_1,
            'WEAPON_2': pg.K_2,
            'WEAPON_3': pg.K_3,
        }
        self.key_state = None
        self.mouse_dx = 0
        self.mouse_dy = 0
        self.mouse_wheel = 0
        self.mouse_buttons = (False, False, False)
        self.events = []
        self.quit = False

    def update(self):
        self.quit = False
        self.mouse_wheel = 0

        self.events = pg.event.get()

        self.mouse_dx, self.mouse_dy = pg.mouse.get_rel()
        self.mouse_buttons = pg.mouse.get_pressed()
        self.key_state = pg.key.get_pressed()

        for event in self.events:
            if event.type == pg.QUIT:
                self.quit = True
            elif event.type == pg.MOUSEWHEEL:
                self.mouse_wheel = event.y
                print(self.mouse_wheel)

    def key_down(self, key_name):
        return self.key_state[self.keys_map[key_name]]

    def mouse_left_pressed(self):
        return self.mouse_buttons[0]

