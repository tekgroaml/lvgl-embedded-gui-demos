"""Legacy Pygame launcher; native/shared implementation lives in common/."""
import argparse
import math
import os
from pathlib import Path
import sys

from common.theme import BG, PANEL, TEXT, MUTED, CYAN, RED, AMBER
from common.telemetry import Telemetry
from scenes.automotive_industrial.model import TelemetrySource


class Painter:
    """Draw in 480-unit coordinates, scaled to the configured square panel."""
    def __init__(self, pygame, surface):
        self.pg, self.surface = pygame, surface
        self.scale = surface.get_width()/480
        self.fonts = {}

    def point(self, x, y): return round(x*self.scale), round(y*self.scale)

    def rect(self, color, bounds, width=0, radius=0):
        x, y, w, h = bounds
        self.pg.draw.rect(self.surface, color, self.pg.Rect(*self.point(x, y), *self.point(w, h)),
                          max(1, round(width*self.scale)) if width else 0, border_radius=round(radius*self.scale))

    def line(self, color, a, b, width=1):
        self.pg.draw.line(self.surface, color, self.point(*a), self.point(*b), max(1, round(width*self.scale)))

    def circle(self, color, xy, radius, width=0):
        self.pg.draw.circle(self.surface, color, self.point(*xy), round(radius*self.scale), max(1, round(width*self.scale)) if width else 0)

    def text(self, value, xy, size=20, color=TEXT, center=True):
        pixels = max(8, round(size*self.scale))
        if pixels not in self.fonts:
            self.fonts[pixels] = self.pg.font.Font(None, pixels)
        rendered = self.fonts[pixels].render(str(value), True, color)
        rect = rendered.get_rect(center=self.point(*xy)) if center else rendered.get_rect(topleft=self.point(*xy))
        self.surface.blit(rendered, rect)

    def polar(self, radius, degrees, center=(240, 240)):
        a = math.radians(degrees)
        return center[0]+radius*math.cos(a), center[1]+radius*math.sin(a)


def run(primary, argv=None):
    p = argparse.ArgumentParser(description="Modern instrumentation on a square or SBS HDMI canvas")
    p.add_argument('--size', type=int, default=480)
    p.add_argument('--fps', type=int, default=60)
    p.add_argument('--windowed', action='store_true')
    p.add_argument('--sbs', action='store_true', help='One wide window: automotive left, industrial right')
    p.add_argument('--display', type=int, default=0)
    p.add_argument('--headless', action='store_true')
    p.add_argument('--frames', type=int, default=0)
    p.add_argument('--screenshot', type=Path)
    p.add_argument('--input-file', type=Path, help='JSON snapshot updated atomically by a telemetry adapter')
    a = p.parse_args(argv)
    if not 128 <= a.size <= 2160 or not 10 <= a.fps <= 240 or a.frames < 0:
        p.error('Use size 128..2160, FPS 10..240 and a nonnegative frame limit.')
    if a.headless and not a.frames: p.error('Headless mode requires --frames N.')
    if a.headless: os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    try: import pygame
    except ImportError: p.exit(1, 'Pygame is missing. Run ./setup.sh --install-only first.\n')
    from gauges.automotive_gauge import AutomotiveGauge
    from gauges.industrial_panel import IndustrialPanel
    pygame.display.init(); pygame.font.init()
    try:
        width = a.size * (2 if a.sbs else 1)
        desktops = pygame.display.get_desktop_sizes()
        if not 0 <= a.display < len(desktops): raise ValueError('Selected SDL display does not exist.')
        if not a.windowed and not a.headless and desktops[a.display] != (width, a.size):
            raise ValueError(f'Configure the desktop to {width}x{a.size} at 100% scale or use --windowed.')
        flags = 0 if a.windowed or a.headless else pygame.FULLSCREEN
        screen = pygame.display.set_mode((width, a.size), flags, display=a.display)
        pygame.display.set_caption('Instrumentation | Space: pause | Tab: switch | Esc: exit')
        pygame.mouse.set_visible(a.windowed)
        square = pygame.Surface((a.size, a.size))
        painter = Painter(pygame, square)
        automotive, industrial = AutomotiveGauge(), IndustrialPanel()
        source = TelemetrySource(a.input_file)
        clock = pygame.time.Clock()
        frame, elapsed, selected = 0, 0.0, primary
        paused, running = False, True
        snapshot = source.read(0)
        print(f'Rendering {width}x{a.size}; telemetry={"JSON input" if a.input_file else "simulation"}. Press Esc to exit.')
        while running:
            dt = 1/a.fps if a.headless else min(clock.tick(a.fps)/1000, .1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q): running = False
                    elif event.key == pygame.K_SPACE and a.input_file is None: paused = not paused
                    elif event.key == pygame.K_TAB: selected = 'industrial' if selected == 'automotive' else 'automotive'
            if not paused:
                elapsed += dt
                snapshot = source.read(elapsed)
                automotive.update(dt, snapshot)
                industrial.update(dt, snapshot)
            views = [automotive, industrial] if a.sbs else [automotive if selected == 'automotive' else industrial]
            for index, view in enumerate(views):
                square.fill(BG)
                view.draw(painter, snapshot, paused)
                screen.blit(square, (index*a.size, 0))
            pygame.display.flip()
            frame += 1
            if a.frames and frame >= a.frames: break
        if a.screenshot:
            a.screenshot.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(screen, str(a.screenshot))
        return 0
    except (OSError, ValueError, pygame.error) as exc:
        print(f'Instrumentation error: {exc}', file=sys.stderr); return 1
    finally: pygame.quit()
