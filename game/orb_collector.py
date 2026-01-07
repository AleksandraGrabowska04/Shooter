"""
Orb Collector - Demo game for hand control integration.

Move a drone to collect energy orbs and avoid hazards.
Fist triggers a pulse. Head tilt cycles pulse modes. Head nod recharges energy.
"""

import math
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import pygame

from .connector import GameCommand


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS = 60

# Theme colors
NAVY = (12, 16, 28)
MIDNIGHT = (24, 32, 52)
PANEL_BG = (20, 26, 38)
PANEL_BORDER = (70, 90, 120)
TEXT_PRIMARY = (230, 238, 255)
TEXT_MUTED = (160, 180, 210)
ACCENT_GOLD = (255, 193, 99)
ACCENT_BLUE = (120, 200, 255)
ACCENT_RED = (240, 90, 90)
WHITE = (255, 255, 255)


@dataclass
class Vector2:
    """Simple 2D vector utility."""
    x: float
    y: float

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2":
        return Vector2(self.x * scalar, self.y * scalar)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalize(self) -> "Vector2":
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def to_tuple(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))


class Starfield:
    """Background starfield for depth and motion."""

    def __init__(self, width: int, height: int, count: int = 90):
        self.width = width
        self.height = height
        self.stars = [self._create_star(True) for _ in range(count)]

    def _create_star(self, random_y: bool) -> Dict[str, float]:
        y = random.uniform(0, self.height) if random_y else -random.uniform(0, self.height * 0.3)
        return {
            "x": random.uniform(0, self.width),
            "y": y,
            "speed": random.uniform(18.0, 70.0),
            "radius": random.uniform(1.0, 2.2),
            "brightness": random.uniform(150.0, 235.0)
        }

    def update(self, dt: float) -> None:
        for star in self.stars:
            star["y"] += star["speed"] * dt
            if star["y"] > self.height:
                star.update(self._create_star(False))

    def draw(self, screen: pygame.Surface) -> None:
        for star in self.stars:
            brightness = int(star["brightness"])
            color = (brightness, brightness, brightness)
            pygame.draw.circle(
                screen,
                color,
                (int(star["x"]), int(star["y"])),
                int(star["radius"])
            )


@dataclass(frozen=True)
class PulseMode:
    """Pulse mode settings."""
    name: str
    radius: float
    cost: int
    cooldown: float
    color: Tuple[int, int, int]


class Pulse:
    """Expanding pulse that clears hazards."""

    def __init__(self, position: Vector2, mode: PulseMode):
        self.position = Vector2(position.x, position.y)
        self.radius = 8.0
        self.max_radius = mode.radius
        self.speed = mode.radius * 1.8
        self.color = mode.color
        self.alive = True

    def update(self, dt: float) -> None:
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.alive = False

    def draw(self, screen: pygame.Surface) -> None:
        alpha = max(0, 180 - int(self.radius * 0.8))
        if alpha <= 0:
            return
        pulse_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(
            pulse_surface,
            (*self.color, alpha),
            (int(self.radius), int(self.radius)),
            int(self.radius),
            2
        )
        screen.blit(pulse_surface, (self.position.x - self.radius, self.position.y - self.radius))


class Orb:
    """Collectible energy orb."""

    def __init__(self, x: float, y: float):
        self.position = Vector2(x, y)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(10.0, 30.0)
        self.velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
        self.size = random.randint(6, 10)
        self.value = 15

    def update(self, dt: float) -> None:
        self.position = self.position + self.velocity * dt
        if self.position.x < 10:
            self.position.x = 10
            self.velocity.x *= -1
        if self.position.x > WINDOW_WIDTH - 10:
            self.position.x = WINDOW_WIDTH - 10
            self.velocity.x *= -1
        if self.position.y < 10:
            self.position.y = 10
            self.velocity.y *= -1
        if self.position.y > WINDOW_HEIGHT - 10:
            self.position.y = WINDOW_HEIGHT - 10
            self.velocity.y *= -1

    def draw(self, screen: pygame.Surface) -> None:
        glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*ACCENT_BLUE, 90),
            (self.size * 2, self.size * 2),
            self.size * 2
        )
        screen.blit(glow_surface, (self.position.x - self.size * 2, self.position.y - self.size * 2))
        pygame.draw.circle(screen, ACCENT_BLUE, self.position.to_tuple(), self.size)


class Hazard:
    """Hazard that drifts downward."""

    def __init__(self, x: float, y: float):
        self.position = Vector2(x, y)
        self.velocity = Vector2(random.uniform(-20.0, 20.0), random.uniform(60.0, 140.0))
        self.size = random.randint(10, 16)
        self.alive = True

    def update(self, dt: float) -> None:
        self.position = self.position + self.velocity * dt
        if self.position.y > WINDOW_HEIGHT + 30:
            self.alive = False

    def draw(self, screen: pygame.Surface) -> None:
        glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*ACCENT_RED, 70),
            (self.size * 2, self.size * 2),
            self.size * 2
        )
        screen.blit(glow_surface, (self.position.x - self.size * 2, self.position.y - self.size * 2))
        pygame.draw.circle(screen, ACCENT_RED, self.position.to_tuple(), self.size)
        pygame.draw.circle(screen, WHITE, self.position.to_tuple(), self.size, 2)


class Drone:
    """Player drone controlled by gesture input."""

    def __init__(self, x: float, y: float):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.angle = -90.0
        self.angle_velocity = 0.0
        self.size = 18
        self.color = ACCENT_GOLD

        self.max_speed = 300
        self.friction = 0.86
        self.acceleration_scale = 800
        self.turn_accel = 220
        self.turn_friction = 0.7

    def apply_movement(self, vector: Tuple[float, float], velocity: Tuple[float, float]) -> None:
        self.acceleration = Vector2(vector[0] * self.acceleration_scale, vector[1] * self.acceleration_scale)
        self.velocity.x += velocity[0] * 0.2
        self.velocity.y += velocity[1] * 0.2

    def apply_turn(self, turn: float) -> None:
        self.angle_velocity += turn * self.turn_accel
        self.angle_velocity = max(-360, min(360, self.angle_velocity))

    def update(self, dt: float) -> None:
        self.velocity = self.velocity + self.acceleration * dt
        speed = self.velocity.length()
        if speed > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed

        self.velocity = self.velocity * self.friction
        self.position = self.position + self.velocity * dt
        self.angle += self.angle_velocity * dt
        self.angle_velocity *= self.turn_friction

        if self.position.x < self.size:
            self.position.x = self.size
            self.velocity.x = abs(self.velocity.x) * 0.4
        if self.position.x > WINDOW_WIDTH - self.size:
            self.position.x = WINDOW_WIDTH - self.size
            self.velocity.x = -abs(self.velocity.x) * 0.4
        if self.position.y < self.size:
            self.position.y = self.size
            self.velocity.y = abs(self.velocity.y) * 0.4
        if self.position.y > WINDOW_HEIGHT - self.size:
            self.position.y = WINDOW_HEIGHT - self.size
            self.velocity.y = -abs(self.velocity.y) * 0.4

        self.acceleration = self.acceleration * 0.1

    def stop(self) -> None:
        self.acceleration = Vector2(0, 0)
        self.velocity = Vector2(0, 0)

    def draw(self, screen: pygame.Surface) -> None:
        angle_rad = math.radians(self.angle)
        forward = Vector2(math.cos(angle_rad), math.sin(angle_rad))
        right = Vector2(-forward.y, forward.x)

        nose = self.position + forward * self.size
        left = self.position - forward * self.size * 0.7 + right * self.size * 0.6
        right_pt = self.position - forward * self.size * 0.7 - right * self.size * 0.6

        glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*self.color, 80),
            (self.size * 2, self.size * 2),
            self.size * 2
        )
        screen.blit(glow_surface, (self.position.x - self.size * 2, self.position.y - self.size * 2))

        pygame.draw.polygon(screen, self.color, [nose.to_tuple(), left.to_tuple(), right_pt.to_tuple()])
        pygame.draw.circle(screen, WHITE, self.position.to_tuple(), 3)


class OrbCollectorGame:
    """
    Orb Collector demo game that integrates with the control connector.
    """

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Orb Collector")
        self.clock = pygame.time.Clock()

        self.background_surface = self._create_background_surface()
        self.starfield = Starfield(WINDOW_WIDTH, WINDOW_HEIGHT, count=90)

        self.player = Drone(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.orbs: List[Orb] = []
        self.hazards: List[Hazard] = []
        self.pulses: List[Pulse] = []

        self.score = 0
        self.lives = 3
        self.running = True
        self.paused = False
        self.control_active = False

        self.modes = [
            PulseMode("pulse", radius=120, cost=22, cooldown=0.4, color=ACCENT_GOLD),
            PulseMode("nova", radius=180, cost=35, cooldown=0.7, color=ACCENT_BLUE),
            PulseMode("burst", radius=90, cost=15, cooldown=0.25, color=ACCENT_RED),
        ]
        self.current_mode_index = 0

        self.max_energy = 100
        self.energy = self.max_energy
        self.recharging = False
        self.recharge_rate = 30.0
        self.last_pulse_time = 0.0

        self.orb_target_count = 6
        self.hazard_spawn_interval = 1.3
        self.last_hazard_spawn = 0.0

        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)

        self.screen_shake = 0.0

    def _create_background_surface(self) -> pygame.Surface:
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            t = y / max(1, WINDOW_HEIGHT - 1)
            r = int(NAVY[0] * (1 - t) + MIDNIGHT[0] * t)
            g = int(NAVY[1] * (1 - t) + MIDNIGHT[1] * t)
            b = int(NAVY[2] * (1 - t) + MIDNIGHT[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        return surface

    def handle_game_command(self, command: GameCommand) -> None:
        """Handle game commands from control connector."""
        if command.command_type == "MOVEMENT":
            self._handle_movement_command(command.data)
        elif command.command_type == "ROTATION":
            self._handle_rotation_command(command.data)
        elif command.command_type == "SHOOT":
            self._handle_shoot_command()
        elif command.command_type == "MODE_CHANGE":
            self._handle_mode_change(command.data)
        elif command.command_type == "RELOAD":
            self._start_recharge()
        elif command.command_type == "DEACTIVATE":
            self.control_active = False
            self.player.stop()

    def _handle_movement_command(self, data: Dict[str, Any]) -> None:
        if data.get("stop"):
            self.control_active = False
            self.player.stop()
            return

        vector = data.get("vector", (0.0, 0.0))
        velocity = data.get("velocity", (0.0, 0.0))
        if isinstance(vector, (list, tuple)) and len(vector) >= 2:
            vector = (float(vector[0]), float(vector[1]))
        else:
            vector = (0.0, 0.0)

        if isinstance(velocity, (list, tuple)) and len(velocity) >= 2:
            velocity = (float(velocity[0]), float(velocity[1]))
        else:
            velocity = (0.0, 0.0)

        self.control_active = True
        self.player.apply_movement(vector, velocity)

    def _handle_rotation_command(self, data: Dict[str, Any]) -> None:
        turn = float(data.get("turn", 0.0))
        self.player.apply_turn(turn)

    def _handle_shoot_command(self) -> None:
        mode = self.modes[self.current_mode_index]
        current_time = time.time()
        if self.recharging:
            return
        if current_time - self.last_pulse_time < mode.cooldown:
            return
        if self.energy < mode.cost:
            return

        self.pulses.append(Pulse(self.player.position, mode))
        self.energy = max(0, self.energy - mode.cost)
        self.last_pulse_time = current_time

    def _handle_mode_change(self, data: Dict[str, Any]) -> None:
        direction = data.get("change_direction", "next")
        if direction == "next":
            self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
        else:
            self.current_mode_index = (self.current_mode_index - 1) % len(self.modes)

        self.player.color = self.modes[self.current_mode_index].color

    def _start_recharge(self) -> None:
        if self.energy < self.max_energy:
            self.recharging = True

    def _spawn_orb(self) -> None:
        x = random.uniform(60, WINDOW_WIDTH - 60)
        y = random.uniform(60, WINDOW_HEIGHT - 120)
        self.orbs.append(Orb(x, y))

    def _spawn_hazard(self) -> None:
        x = random.uniform(40, WINDOW_WIDTH - 40)
        y = random.uniform(-80, -20)
        self.hazards.append(Hazard(x, y))

    def update(self, dt: float) -> None:
        if self.paused:
            return

        self.starfield.update(dt)
        self.player.update(dt)

        for orb in self.orbs:
            orb.update(dt)

        for hazard in self.hazards:
            hazard.update(dt)

        for pulse in self.pulses:
            pulse.update(dt)

        self.hazards = [h for h in self.hazards if h.alive]
        self.pulses = [p for p in self.pulses if p.alive]

        while len(self.orbs) < self.orb_target_count:
            self._spawn_orb()

        current_time = time.time()
        if current_time - self.last_hazard_spawn >= self.hazard_spawn_interval:
            self._spawn_hazard()
            self.last_hazard_spawn = current_time
            if self.hazard_spawn_interval > 0.6:
                self.hazard_spawn_interval *= 0.992

        self._handle_collisions()
        self._update_recharge(dt)

        if self.lives <= 0:
            self.running = False

        self.screen_shake = max(0.0, self.screen_shake - dt * 6.0)

    def _handle_collisions(self) -> None:
        player_radius = self.player.size

        for orb in self.orbs[:]:
            if (orb.position - self.player.position).length() < orb.size + player_radius:
                self.score += orb.value
                self.orbs.remove(orb)

        for hazard in self.hazards[:]:
            if (hazard.position - self.player.position).length() < hazard.size + player_radius:
                self.lives -= 1
                hazard.alive = False
                self.screen_shake = 1.0

        for pulse in self.pulses:
            for hazard in self.hazards[:]:
                if (hazard.position - pulse.position).length() < pulse.radius:
                    hazard.alive = False
                    self.score += 8

    def _update_recharge(self, dt: float) -> None:
        if not self.recharging:
            return
        self.energy += self.recharge_rate * dt
        if self.energy >= self.max_energy:
            self.energy = self.max_energy
            self.recharging = False

    def draw(self) -> None:
        self.screen.blit(self.background_surface, (0, 0))
        self.starfield.draw(self.screen)

        shake_x = int(random.uniform(-6, 6) * self.screen_shake)
        shake_y = int(random.uniform(-6, 6) * self.screen_shake)

        temp_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for pulse in self.pulses:
            pulse.draw(temp_surface)
        for orb in self.orbs:
            orb.draw(temp_surface)
        for hazard in self.hazards:
            hazard.draw(temp_surface)
        self.player.draw(temp_surface)

        self.screen.blit(temp_surface, (shake_x, shake_y))

        self._draw_ui()

        if self.paused:
            self._draw_pause_overlay()

        pygame.display.flip()

    def _draw_ui(self) -> None:
        self._draw_panels()
        self._draw_stats()
        self._draw_energy()
        self._draw_control_status()
        self._draw_instructions()

    def _draw_panels(self) -> None:
        left_panel = pygame.Rect(8, 8, 250, 210)
        right_panel = pygame.Rect(WINDOW_WIDTH - 240, 8, 230, 110)
        bottom_panel = pygame.Rect(8, WINDOW_HEIGHT - 140, WINDOW_WIDTH - 16, 130)

        for panel in (left_panel, right_panel, bottom_panel):
            panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
            panel_surface.fill((*PANEL_BG, 175))
            self.screen.blit(panel_surface, panel.topleft)
            pygame.draw.rect(self.screen, PANEL_BORDER, panel, 2)

    def _draw_stats(self) -> None:
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_PRIMARY)
        self.screen.blit(score_text, (16, 16))

        lives_text = self.font.render(f"Lives: {self.lives}", True, TEXT_PRIMARY)
        self.screen.blit(lives_text, (16, 52))

        mode = self.modes[self.current_mode_index]
        mode_text = self.font.render(f"Mode: {mode.name.upper()}", True, mode.color)
        self.screen.blit(mode_text, (16, 88))

    def _draw_energy(self) -> None:
        label = self.small_font.render("Energy", True, TEXT_MUTED)
        self.screen.blit(label, (16, 130))

        bar_width = 180
        bar_height = 10
        bar_x = 16
        bar_y = 150
        pygame.draw.rect(self.screen, (40, 50, 70), (bar_x, bar_y, bar_width, bar_height))

        fill = int(bar_width * (self.energy / self.max_energy))
        color = ACCENT_GOLD if self.energy > 30 else ACCENT_RED
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill, bar_height))

        if self.recharging:
            recharge_text = self.small_font.render("Recharging...", True, ACCENT_GOLD)
            self.screen.blit(recharge_text, (16, 168))

    def _draw_control_status(self) -> None:
        status_color = ACCENT_BLUE if self.control_active else ACCENT_RED
        status_text = "Input: ACTIVE" if self.control_active else "Input: INACTIVE"
        text = self.small_font.render(status_text, True, status_color)
        self.screen.blit(text, (WINDOW_WIDTH - 220, 16))

    def _draw_instructions(self) -> None:
        instructions = [
            "CONTROLS",
            "Hand: move drone  Fist: pulse",
            "Head tilt: cycle mode  Head nod: recharge",
            "Head turn: rotate",
            "KEYBOARD",
            "WASD or arrows: move",
            "Space: pulse  R: recharge",
            "Q/E: cycle mode  P: pause"
        ]

        start_y = WINDOW_HEIGHT - 125
        for i, line in enumerate(instructions):
            if line in ("CONTROLS", "KEYBOARD"):
                color = ACCENT_BLUE
            else:
                color = TEXT_MUTED
            text = self.small_font.render(line, True, color)
            self.screen.blit(text, (16, start_y + i * 16))

    def _draw_pause_overlay(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(NAVY)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("PAUSED", True, TEXT_PRIMARY)
        text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)

    def handle_pygame_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown_event(event)

    def _handle_keydown_event(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_SPACE:
            self._handle_shoot_command()
        elif event.key == pygame.K_p:
            self.paused = not self.paused
        elif event.key == pygame.K_r:
            self._start_recharge()
        elif event.key == pygame.K_q:
            self._handle_mode_change({"change_direction": "previous"})
        elif event.key == pygame.K_e:
            self._handle_mode_change({"change_direction": "next"})

        self._handle_movement_keys(event)

    def _handle_movement_keys(self, event: pygame.event.Event) -> None:
        if self.control_active:
            return

        speed = 0.8
        if event.key in (pygame.K_w, pygame.K_UP):
            self.player.apply_movement((0.0, -speed), (0.0, -120.0))
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.player.apply_movement((0.0, speed), (0.0, 120.0))
        elif event.key in (pygame.K_a, pygame.K_LEFT):
            self.player.apply_movement((-speed, 0.0), (-120.0, 0.0))
        elif event.key in (pygame.K_d, pygame.K_RIGHT):
            self.player.apply_movement((speed, 0.0), (120.0, 0.0))

    def run(self) -> None:
        print("Starting Orb Collector")
        print("Use hand gestures or keyboard controls if hand control is inactive")

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_pygame_event(event)
            self.update(dt)
            self.draw()

        print(f"Game Over! Final Score: {self.score}")
        pygame.quit()

    def get_game_stats(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'lives': self.lives,
            'orbs': len(self.orbs),
            'hazards': len(self.hazards),
            'pulses': len(self.pulses),
            'control_active': self.control_active,
            'paused': self.paused,
            'fps': int(self.clock.get_fps())
        }
