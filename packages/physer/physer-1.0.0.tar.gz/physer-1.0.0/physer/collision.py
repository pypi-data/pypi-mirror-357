from .collider import Collider
import pygame

def resolve_collisions(self):
    colliders = self._colliders
    n = len(colliders)

    # Reset collision state
    for c in colliders:
        c._previous_collisions = c._current_collisions
        c._current_collisions = set()

    # Detect and resolve collisions
    for i in range(n):
        a = colliders[i]
        for j in range(i + 1, n):
            b = colliders[j]

            # Skip if they don't collide
            if not a.rect.colliderect(b.rect):
                continue

            # Skip if collision classes exist and they ignore each other
            if a.collision_class and b.collision_class:
                a_class = self._collision_classes.get(a.collision_class, {})
                b_class = self._collision_classes.get(b.collision_class, {})
                if b.collision_class in a_class.get("ignores", []):
                    continue
                if a.collision_class in b_class.get("ignores", []):
                    continue

            # Register collision
            a._current_collisions.add(b)
            b._current_collisions.add(a)

            # Call onStay or onEnter
            if b in a._previous_collisions:
                if a.on_stay: a.on_stay(b.object)
                if b.on_stay: b.on_stay(a.object)
            else:
                if a.on_enter: a.on_enter(b.object)
                if b.on_enter: b.on_enter(a.object)

            if a.type == "sensor" or b.type == "sensor":
                continue

            # Determine collision behavior based on types
            pair = (a.type, b.type)

            if "static" in pair:
                # Static vs moving
                static_collider = a if a.type == "static" else b
                other_collider = b if a.type == "static" else a
                __separate_collider(other_collider, static_collider)

            elif pair == ("dynamic", "dynamic"):
                __separate_both(a, b)

            elif "dynamic" in pair and "kinematic" in pair:
                if a.type == "dynamic":
                    __separate_collider(a, b)
                else:
                    __separate_collider(b, a)

    # Handle onExit for things no longer colliding
    for c in colliders:
        exited = c._previous_collisions - c._current_collisions
        for other in exited:
            if c.on_exit:
                c.on_exit(other.object)

def __separate_collider(mover: Collider, obstacle: Collider):
    # Move mover out of obstacle along shortest axis of overlap
    overlap = mover.rect.clip(obstacle.rect)

    if overlap.width < overlap.height:
        # Separate horizontally
        if mover.rect.centerx < obstacle.rect.centerx:
            mover.rect.right = obstacle.rect.left
        else:
            mover.rect.left = obstacle.rect.right

        # Stop horizontal velocity to prevent sticking
        mover.velocity.x = 0
    else:
        # Separate vertically
        if mover.rect.centery < obstacle.rect.centery:
            mover.rect.bottom = obstacle.rect.top
        else:
            mover.rect.top = obstacle.rect.bottom

        # Stop vertical velocity to prevent sticking
        mover.velocity.y = 0

def __separate_both(a: Collider, b: Collider):
    overlap = a.rect.clip(b.rect)

    if overlap.width < overlap.height:
        move_dist = overlap.width / 2
        if a.rect.centerx < b.rect.centerx:
            a.rect.right -= move_dist
            b.rect.left += move_dist
        else:
            a.rect.left += move_dist
            b.rect.right -= move_dist

        # Zero only velocity along collision axis (projected)
        __zero_velocity_along_axis(a, pygame.Vector2(1, 0))
        __zero_velocity_along_axis(b, pygame.Vector2(-1, 0))
    else:
        move_dist = overlap.height / 2
        if a.rect.centery < b.rect.centery:
            a.rect.bottom -= move_dist
            b.rect.top += move_dist
        else:
            a.rect.top += move_dist
            b.rect.bottom -= move_dist

        __zero_velocity_along_axis(a, pygame.Vector2(0, 1))
        __zero_velocity_along_axis(b, pygame.Vector2(0, -1))

def __zero_velocity_along_axis(collider: Collider, axis: pygame.Vector2):
    # Project velocity onto axis
    velocity_along_axis = collider.velocity.dot(axis)
    if velocity_along_axis > 0:
        # Remove velocity component along axis
        collider.velocity -= axis * velocity_along_axis