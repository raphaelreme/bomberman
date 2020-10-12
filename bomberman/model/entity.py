"""Provides classes for all entities of the game"""

from __future__ import annotations

import enum
from typing import List, Optional, Set

from ..designpattern import observable
from . import events
from . import maze


class Damage:
    """Damage done to entities

    Two types: Damage from bombs. And damage from the enemies.
    """
    class Type(enum.Enum):
        ENEMIES = 0
        BOMBS = 1

    def __init__(self, damage: int, type_: Type):
        self.damage = damage
        self.type = type_


class Position:
    """Position of entities in the maze."""
    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j

    def __add__(self, other: object) -> Position:
        if isinstance(other, Direction):
            return Position(self.i + other.value[0], self.j + other.value[1])
        return NotImplemented

    def __str__(self) -> str:
        return str((self.i, self.j))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Position):
            return (self.i, self.j) == (other.i, other.j)
        return NotImplemented


class Direction(enum.Enum):
    """Direction to follow."""
    UP = (-1, 0)
    DOWN = (1, 0)
    RIGHT = (0, 1)
    LEFT = (0, -1)


class EntityClass(type):
    """Type of Entity classes.

    Attr:
        REPR (Optional, str): Static representation of entities in mazes.
            If not provided, the entity will not be represented in a maze represention.
        representation_to_entity_class (Dict[str: EntityClass]): Mapping from class.REPR to class for all
            EntityClass that are representable. (<=> define REPR attr)
    """
    REPR: str
    representation_to_entity_class: dict = {}  #XXX: Typing ?

    def __init__(cls, cls_name: str, bases: tuple, attributes: dict) -> None:
        super().__init__(cls_name, bases, attributes)
        if hasattr(cls, "REPR"):
            representation = cls.REPR
            if representation == " " or representation == "|" or len(representation) > 1:
                raise ValueError(
                    f"Invalid REPR attribute: {representation} of {cls}. "
                    f"Should be a single char and not '{maze.Maze.VOID}' nor '{maze.Maze.SEP}'"
                )
            type(cls).representation_to_entity_class[representation] = cls

class Entity(observable.Observable, metaclass=EntityClass):
    """Anything that is inside the maze.

    Attrs:
        BASE_HEALTH (int): Hp of the entity. When reaching 0, the entity is removed.
            Default to 0 (Removed at the first damage received)
        SIZE (Tuple[int, int]): (# row, # columns) of the entity.
            Default to (1, 1) (One tile large)
        VULNERABILIES (List[Damage.Type]): Vulnerabilies of the entity.
            Default to [] (Cannot take damage and is therefore invulnerable)
        REMOVING_DELAY (int): Time in removing state
            Default to 0 (Immediately removed.)
    """
    BASE_HEALTH = 0
    SIZE = (1, 1)
    VULNERABILITIES: List[Damage.Type] = []
    REMOVING_DELAY: float = 0

    def __init__(self, maze_: maze.Maze, position: Position) -> None:
        """Initialise an entity in the maze.

        Args:
            maze_ (Maze): The maze of the entity.
            position (Tuple[int, int]): Row and column indexes of the entity in the maze.
                If the entity is on several row/columns, it will indicates the top left corner of it.
        """
        super().__init__()
        self.maze = maze_
        self.position = position
        self.health = self.BASE_HEALTH
        self.is_removing = False
        self.removing_delay = self.REMOVING_DELAY

    def update(self, delay: float):
        """Handle time forwarding.

        Args:
            delay (float): Seconds spent since last call.
        """
        if self.is_removing:
            self.removing_delay -= delay
            if self.removing_delay <= 0:
                self.remove()
            else:
                self.changed(events.RemovingEntityEvent(self))

    def hit(self, damage: Damage) -> None:
        if damage.type in self.VULNERABILITIES:
            self.changed(events.HitEntityEvent(self))
            self.health -= damage.damage
            if self.health <= 0:
                self.removing()

    def removing(self) -> None:
        self.is_removing = True

    def remove(self) -> None:
        self.maze.remove_entity(self)


class BreakableWall(Entity):
    REPR = "B"
    VULNERABILITIES = [Damage.Type.BOMBS]
    REMOVING_DELAY = 0.5


class SolideWall(Entity):
    REPR = "S"


class Bomb(Entity):
    VULNERABILITIES = [Damage.Type.BOMBS]
    REMOVING_DELAY = 0
    BASE_TIMEOUT: float = 5
    FAST_TIMEOUT: float = 2

    def __init__(self, player: Player, position: Position) -> None:
        super().__init__(player.maze, position)
        self.player = player
        self.timeout = self.FAST_TIMEOUT if player.fast_bomb else self.BASE_TIMEOUT
        self.radius = player.bomb_radius

    def update(self, delay: float) -> None:
        if not self.is_removing:
            self.timeout -= delay
            if self.timeout <= 0:
                self.removing()
                super().update(-self.timeout)
            else:
                self.changed(events.ForwardTimeEvent(self))

    def removing(self) -> None:
        super().removing()
        self.player.bomb_explodes()
        self.explodes()

    def explodes(self) -> None:  # Create lasers
        pass


class MovingEntity(Entity):
    """Moving entity in the maze.

    Let's split a tile in 100 small steps.
    An entity will move on those step toward another tile.

    Attrs:
        BASE_SPEED (int): Base speed of the entity.
            Default to 3 blocks per second
        BLOCKED_BY (Set[Entity]): Entities that will block thes
    """
    BASE_SPEED = 300
    BLOCKED_BY: Set[EntityClass] = set()

    def __init__(self, maze_: maze.Maze, position: Position) -> None:
        super().__init__(maze_, position)
        self.speed = self.BASE_SPEED
        self.current_direction: Optional[Direction] = None
        self.next_direction: Optional[Direction] = None
        self.next_position: Optional[Position] = None
        self.step = 0
        self.try_moving_since: float = 0

    def set_wanted_direction(self, direction: Optional[Direction]) -> None:
        self.next_direction = direction

    def update(self, delay: float) -> None:
        super().update(delay)
        if self.is_removing:
            return

        if not self.next_position:  # not moving. Can change/set/unset current_direction
            self.current_direction = self.next_direction

        if not self.current_direction:  # Not direction: Maybe we just stopped -> update
            print(self.try_moving_since)
            self.changed(events.MovedEntityEvent(self))
            return

        self.try_moving_since += delay

        if not self.next_position:
            next_position = self.position + self.current_direction
            if self.maze.is_inside(next_position) and not self.maze.contains(tuple(self.BLOCKED_BY), next_position):
                self.next_position = next_position

        if not self.next_position:
            self.changed(events.MovedEntityEvent(self))
            return

        self.step += int(delay * self.speed)
        if self.step >= 100:
            step = self.step - 100
            self.position = self.next_position

            # Reset movement
            self.step = 0
            self.next_position = None
            self.current_direction = None
            self.try_moving_since = 0

            if self.next_direction:
                self.current_direction = self.next_direction
                # self.next_direction = None

                next_position = self.position + self.current_direction
                if self.maze.is_inside(next_position) and not self.maze.contains(tuple(self.BLOCKED_BY), next_position):
                    self.next_position = next_position
                    self.step = step

        self.changed(events.MovedEntityEvent(self))


class Player(MovingEntity):
    """Player entity.

    Moves and drops bombs
    """
    REPR = "P"
    VULNERABILITIES = [Damage.Type.BOMBS, Damage.Type.ENEMIES]
    BASE_HEALTH = 100
    BASE_BOMB_CAPACITY = 6
    BASE_BOMB_RADIUS = 2

    def __init__(self, maze_: maze.Maze, position: Position) -> None:
        super().__init__(maze_, position)

        self.identifier = self.maze.get_player_count()

        self.bomb_capacity = self.BASE_BOMB_CAPACITY
        self.bomb_radius = self.BASE_BOMB_RADIUS
        self.fast_bomb = False

    def bombs(self) -> None:
        bomb_position = self.position
        if self.step > 80:
            bomb_position += self.current_direction

        if self.bomb_capacity > 0:
            if self.maze.contains((Bomb,), bomb_position):
                return
            bomb = Bomb(self, bomb_position)
            self.maze.add_entity(bomb)
            self.bomb_capacity -= 1

    def bomb_explodes(self) -> None:
        self.bomb_capacity += 1

#FIXME: Beurk Could be an object attr ? Or decorated class in order to reference to itself ?
Player.BLOCKED_BY = set([BreakableWall, SolideWall, Player])


class Enemy(MovingEntity):
    """Base class for all enemies."""
    VULNERABILITIES = [Damage.Type.BOMBS]

# FIXME: Beurk
Enemy.BLOCKED_BY = set([BreakableWall, SolideWall, Enemy])
