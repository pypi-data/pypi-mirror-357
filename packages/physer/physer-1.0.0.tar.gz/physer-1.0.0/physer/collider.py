import pygame
from pygame.math import Vector2
from typing import Literal

class Collider():
    def __init__(self, rect: pygame.Rect, manual_update, **kwargs):
        self.rect: pygame.Rect = rect
        self.velocity: Vector2 = Vector2(0,0)
        self.friction: float = 0
        self.collision_class: str = None
        self.type: Literal["static", "dynamic", "kinematic", "sensor"] = "dynamic"
        self.manual_update = manual_update
        self._current_collisions: set[Collider] = set()
        self._previous_collisions: set[Collider] = set()
        self.on_enter: callable = None
        self.on_exit: callable = None
        self.on_stay: callable = None
        self.object: any = self
        self.__dict__.update(kwargs)

    def set_collision_class(self, class_name: str):
        self.collision_class = class_name

    def _update(self, gravity: pygame.Vector2, dt: float):
        self.__update_gravity(gravity, dt)
        self.__finalize_movement(dt)

    def __finalize_movement(self, dt: float):
        if self.type == "dynamic" or self.type == "sensor":
            # Friction
            if self.velocity.length_squared() > 0:
                friction_force = self.velocity.normalize() * (-self.friction)
                self.velocity += friction_force * dt
                # Prevent oscillating around zero
                if self.velocity.length() < 0.01:
                    self.velocity = Vector2(0,0)

            self.rect.center += self.velocity * dt

        elif self.type == "kinematic":
            self.rect.center += self.velocity * dt

        elif self.type == "static":
            pass

    def __update_gravity(self, gravity: pygame.Vector2, dt: float):
        if self.type == "dynamic" or self.type == "sensor":
            self.velocity += gravity * dt