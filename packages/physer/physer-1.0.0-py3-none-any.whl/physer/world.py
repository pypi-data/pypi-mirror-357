import pygame
from pygame.math import Vector2
from typing import List
from .collider import Collider
from .collision import resolve_collisions

class World():
    def __init__(self, gravity: Vector2):
        self.gravity: Vector2 = gravity
        self._colliders: List[Collider] = []
        self._collision_classes: dict[str, dict] = {}

    def new_collider(self, rect: pygame.Rect, manual_update: bool = False, **kwargs) -> Collider:
        collider = Collider(rect, manual_update, **kwargs)
        self._colliders.append(collider)
        return collider
    
    def new_collision_class(self, class_name: str, ignores: list[str] = None, **kwargs):
        if ignores is None:
            ignores = []

        class_data = {
            "ignores": ignores,
            **kwargs
        }
        self._collision_classes[class_name] = class_data
    
    def update(self, dt):
        for collider in self._colliders:
            if collider.manual_update: continue
            collider._update(self.gravity, dt)

        resolve_collisions(self)

    def draw(self, screen, color: tuple[int, int, int, int] = (255, 255, 255, 255), width: int = 1, **kwargs):
        for collider in self._colliders:
            pygame.draw.rect(screen, color, collider.rect, width, **kwargs)