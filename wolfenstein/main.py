import argparse
import os
import sys
import moderngl as mgl

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engine import Engine
from settings import *

# every file is supposed to be commented as solid as possible so that you fucking remember what it fucking does
# TODO: generate requirements.txt file


class Game:
    def __init__(self, use_gestures: bool = False):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, MAJOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, MINOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, DEPTH_SIZE)   # bits for depth

        pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.gc_mode = 'auto'   # automatic garbace collection

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0
        self.use_gestures = use_gestures

        pg.event.set_grab(True)   #locks cursor in window
        pg.mouse.set_visible(False)

        self.is_running = True
        self.fps_value = 0

        self.engine = Engine(self, use_gesture_control=use_gestures)

        self.anim_ticks = 0
        self.anim_event = pg.USEREVENT + 0
        pg.time.set_timer(self.anim_event, SYNC_PULSE)

        self.sound_trigger = False
        self.sound_event = pg.USEREVENT + 1
        pg.time.set_timer(self.sound_event, 750)

    def update(self):
        self.engine.update()
        #
        self.delta_time = self.clock.tick()
        self.time = pg.time.get_ticks() * 0.001
        self.fps_value = int(self.clock.get_fps())
        pg.display.set_caption(f'{self.fps_value}')

    def render(self):
        self.ctx.clear(color=BG_COLOR)
        self.engine.render()
        pg.display.flip()   # display new frame

    def handle_events(self):
        self.anim_ticks, self.sound_trigger = 0, False

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False
            #
            if event.type == self.anim_event:
                if self.use_gestures:
                    self.anim_ticks += 1
                else:
                    self.anim_ticks = 1
            #
            if event.type == self.sound_event:
                self.sound_trigger = True
            #
            self.engine.handle_events(event=event)

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
        self.engine.shutdown()
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Wolfenstein")
    parser.add_argument(
        "--gestures",
        action="store_true",
        help="Enable gesture control integration"
    )
    args = parser.parse_args()

    game = Game(use_gestures=args.gestures)
    game.run()
