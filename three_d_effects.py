"""High-end 2.5D/3D-style visual effects for the Human Body Nutrition Simulator.

This module is intentionally pygame-only so it can be dropped into the existing
Capstone project without adding a large external dependency.  It provides:
- depth/parallax body rendering
- soft organ glow and shadow layers
- specular highlights and rim lighting
- hover lift / scale animation
- breathing and heartbeat motion
- floating depth particles
- glassy selection rings and connecting energy trails

The result is a game-like 3D presentation while keeping the existing nutrition
simulation and controls intact.
"""
import math
import random
import pygame


class DepthCamera:
    """Small camera model that gives the flat pygame scene convincing depth."""
    def __init__(self):
        self.yaw = 0.0
        self.pitch = 0.0
        self.target_yaw = 0.0
        self.target_pitch = 0.0

    def update(self, mouse_pos, center, dt, strength=0.00055):
        dx = mouse_pos[0] - center[0]
        dy = mouse_pos[1] - center[1]
        self.target_yaw = max(-0.18, min(0.18, dx * strength))
        self.target_pitch = max(-0.12, min(0.12, -dy * strength))
        k = min(1.0, dt * 7.0)
        self.yaw += (self.target_yaw - self.yaw) * k
        self.pitch += (self.target_pitch - self.pitch) * k

    def project(self, x, y, depth, center):
        # Perspective-ish parallax: deeper organs move slightly with camera.
        px = x + depth * self.yaw * 85.0
        py = y + depth * self.pitch * 65.0
        scale = 1.0 + depth * 0.025
        return int(center[0] + (px - center[0]) * scale), int(center[1] + (py - center[1]) * scale), scale


class OrganFX:
    """Stateful visual effects for one organ."""
    def __init__(self, name, color, depth=0.0):
        self.name = name
        self.base_color = tuple(color)
        self.depth = depth
        self.hover = 0.0
        self.health_pulse = 0.0
        self.selected = False
        self.energy = 0.0
        self.seed = random.random() * math.tau

    def update(self, dt, hovered=False, selected=False, health=1.0):
        target = 1.0 if hovered else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 10.0)
        self.selected = selected
        self.health_pulse += dt * (2.2 + max(0.0, 1.0 - health) * 2.5)
        self.energy = max(0.0, self.energy - dt * 0.55)

    def trigger_energy(self, amount=1.0):
        self.energy = max(self.energy, amount)

    def _mix(self, a, b, t):
        return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

    def _shade(self):
        # Hover makes the organ brighter; lower health adds a subtle warm shift.
        pulse = (math.sin(self.health_pulse + self.seed) + 1.0) * 0.5
        c = self._mix(self.base_color, (255, 255, 255), 0.10 + self.hover * 0.20)
        c = self._mix(c, (255, 90, 70), (1.0 - min(1.0, self.energy)) * 0.0)
        return c, pulse

    def draw(self, screen, draw_callback, center, radius, mouse_pos=None, health=1.0):
        """Draw layered game-like lighting around an existing organ callback.

        draw_callback(surface, x, y, color, edge_color) should render the actual
        organ geometry. The callback can therefore reuse the project's existing
        anatomically-inspired shapes.
        """
        x, y = center
        c, pulse = self._shade()
        lift = self.hover * (5.0 + self.depth * 3.0)
        y -= lift
        scale = 1.0 + self.hover * 0.055
        r = max(4, int(radius * scale))

        # 1) Deep contact shadow.
        shadow = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shadow_col = (0, 0, 0, int(105 + self.hover * 25))
        pygame.draw.ellipse(shadow, shadow_col,
                            (x-r-int(r*0.22), y+r-int(r*0.05),
                             int(r*2.0), max(3, int(r*0.28))))
        screen.blit(shadow, (0, 0))

        # 2) Ambient aura, only visible around the organ rather than as a flat blob.
        aura = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        aura_alpha = int(18 + self.hover * 28 + self.energy * 38)
        for ring in range(4, 0, -1):
            rr = r + ring * 5
            pygame.draw.ellipse(aura, (*c, max(2, aura_alpha // ring)),
                                (x-rr, y-rr, rr*2, rr*2), max(1, int(3*ring/2)))
        screen.blit(aura, (0, 0))

        # 3) Existing anatomical geometry.
        edge = self._mix(c, (235, 245, 255), 0.42)
        draw_callback(screen, x, y, c, edge)

        # 4) Fake 3D bevel: offset translucent silhouette + highlight rim.
        rim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(rim, (255, 255, 255, int(16 + self.hover * 35)),
                            (x-r+2, y-r+2, max(2, r*2-4), max(2, r*2-4)),
                            max(1, int(2 + self.hover * 2)))
        pygame.draw.arc(rim, (255, 255, 255, int(45 + self.hover * 75)),
                        (x-r, y-r, r*2, r*2), math.radians(205), math.radians(320),
                        max(1, int(2 + self.hover * 2)))
        screen.blit(rim, (0, 0))

        # 5) Selection ring with a pulsing sweep.
        if self.selected or self.hover > 0.5:
            ring = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            rr = r + 10 + int(math.sin(self.health_pulse * 1.2) * 2)
            pygame.draw.arc(ring, (*c, 180), (x-rr, y-rr, rr*2, rr*2),
                            -1.1, 2.3, 2)
            pygame.draw.arc(ring, (255, 255, 255, 110), (x-rr-4, y-rr-4, (rr+4)*2, (rr+4)*2),
                            2.6, 4.8, 1)
            screen.blit(ring, (0, 0))

        # 6) Tiny floating motes sell the depth of the scene.
        if self.selected or self.energy > 0.15:
            fx = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            for i in range(6):
                a = self.health_pulse * (0.55 + i * 0.07) + self.seed + i
                px = x + math.cos(a) * (r + 8 + i * 3)
                py = y + math.sin(a * 1.17) * (r * 0.65 + i * 2)
                pr = 1 + (i % 2)
                pygame.draw.circle(fx, (*c, 120), (int(px), int(py)), pr)
            screen.blit(fx, (0, 0))


def draw_3d_body_backdrop(screen, center, top, bottom, t, camera):
    """Draw a subtle volumetric body silhouette behind the organs."""
    cx = center[0]
    cy = (top + bottom) // 2
    h = bottom - top
    w = max(70, int(h * 0.28))

    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    # Multiple silhouettes create a soft depth field.
    for i in range(8, 0, -1):
        depth = i / 8.0
        wobble = math.sin(t * 0.7 + i) * 1.5
        alpha = int(4 + (8-i) * 2.5)
        rrw = int(w * (1.0 + depth * 0.08))
        rrh = int(h * (1.0 + depth * 0.03))
        pygame.draw.ellipse(layer, (55, 80, 130, alpha),
                            (cx-rrw//2+int(camera.yaw*80*depth),
                             cy-rrh//2+int(camera.pitch*60*depth), rrw, rrh))
    screen.blit(layer, (0, 0))


def draw_breathing_grid(screen, center, radius, t, color=(90, 130, 190)):
    """Volumetric scan grid behind the body, like a modern game HUD."""
    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    cx, cy = center
    for i in range(-4, 5):
        off = i * radius * 0.22
        pygame.draw.arc(layer, (*color, 22),
                        (cx-radius+off, cy-radius*1.45, radius*2-off*2, radius*2.9),
                        0.25 + math.sin(t)*0.02, math.pi-0.25, 1)
    for j in range(-3, 4):
        yy = cy + j * radius * 0.28 + math.sin(t * 0.8 + j) * 2
        pygame.draw.line(layer, (*color, 18), (cx-radius, int(yy)), (cx+radius, int(yy)), 1)
    screen.blit(layer, (0, 0))


def draw_energy_trail(screen, points, color, progress, width=3):
    """Animated nutrient/oxygen energy trail connecting organs."""
    if len(points) < 2:
        return
    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    # Draw a dim base path.
    pygame.draw.lines(layer, (*color, 35), False, points, max(1, width))
    n = max(2, int((len(points)-1) * max(0.0, min(1.0, progress))))
    active = points[:n+1]
    pygame.draw.lines(layer, (*color, 170), False, active, width + 1)
    for i, p in enumerate(active):
        if i % 2 == 0:
            pygame.draw.circle(layer, (*color, 155), p, max(1, width-1))
    screen.blit(layer, (0, 0))
