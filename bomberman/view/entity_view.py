"""Handle entities of the maze."""

from __future__ import annotations

from typing import List, Tuple, cast

from . import TILE_SIZE, inflate_to_reality
from . import view
from ..designpattern import event
from ..designpattern import observer
from ..model import entity
from ..model import events


class EntityView(view.Sprite, observer.Observer):
    """Base view for entities. Let's only use Sprite views.

    It observes an entity.

    Attrs: (Please refer to view.Sprite to have infos about other attributes.)
        PRIORITY (int): Priority in display. (The small priority. display first)
        FILE_NAME (str): File in the image folder where the sprite for this view is stored.
        REMOVING_STEPS (List[Tuple[int, int]]): List of the position of sprites for the removing steps.
    """
    PRIORITY = 0
    FILE_NAME: str
    SPRITE_SIZE = TILE_SIZE
    REMOVING_STEPS: List[Tuple[int, int]] = []

    def __init__(self, entity_: entity.Entity) -> None:
        image_total_size = (self.SPRITE_SIZE[0] * self.COLUMNS, self.SPRITE_SIZE[1] * self.ROWS)
        super().__init__(
            view.load_image(self.FILE_NAME, image_total_size),
            inflate_to_reality((entity_.position.i, entity_.position.j)),
        )
        self.entity = entity_
        self.entity.add_observer(self)
        self.removing_steps = self.REMOVING_STEPS

    def notify(self, event_: event.Event) -> None:
        if event_.handled:
            return

        if isinstance(event_, events.RemovingEntityEvent):
            if not self.entity.is_removing:
                print("WARNING: removing event without removing state:", self)
            event_.handled = True

            if not self.entity.REMOVING_DELAY or not self.removing_steps:
                return

            step = 1 - self.entity.removing_delay / self.entity.REMOVING_DELAY
            stage_length = 1 / len(self.removing_steps)

            self.select_sprite(*self.removing_steps[int(step/stage_length)])

    @staticmethod
    def from_entity(entity_: entity.Entity) -> EntityView:
        return {
            entity.SolideWall: SolideWallView,
            entity.BreakableWall: BreakableWallView,
            entity.Bomb: BombView,
            entity.Player: PlayerView,
        }[type(entity_)](entity_)

    def __lt__(self, other) -> bool:
        if isinstance(other, EntityView):
            return self.PRIORITY < other.PRIORITY
        return NotImplemented


class SolideWallView(EntityView):
    FILE_NAME = "solide_wall.png"
    ROWS = 1
    COLUMNS = 8

    def __init__(self, entity_: entity.SolideWall) -> None:
        super().__init__(entity_)
        # Select according to maze level ?
        self.style = 0
        self.select_sprite(0, self.style)


class BreakableWallView(EntityView):
    FILE_NAME = "breakable_wall.png"
    ROWS = 8
    COLUMNS = 4
    REMOVING_STEPS = [(0, 1), (0, 2), (0, 3)]

    def __init__(self, entity_: entity.BreakableWall) -> None:
        super().__init__(entity_)
        # Select according to maze level ?
        self.style = 0
        self.removing_steps = [(self.style, index[1]) for index in self.REMOVING_STEPS]
        self.select_sprite(self.style, 0)


class BombView(EntityView):
    FILE_NAME = "bomb.png"
    ROWS = 1
    COLUMNS = 3
    RATE = 0.3
    FAST_RATE = 0.05

    def __init__(self, entity_: entity.Bomb) -> None:
        super().__init__(entity_)
        self.select_sprite(0, 0)

    def notify(self, event_: event.Event) -> None:
        super().notify(event_)
        if event_.handled:
            return

        if isinstance(event_, events.ForwardTimeEvent):
            bomb = cast(entity.Bomb, event_.entity)
            if bomb.timeout < bomb.FAST_TIMEOUT:
                index = int((bomb.BASE_TIMEOUT - bomb.timeout) / self.FAST_RATE)
                self.select_sprite(0, 1 + (index % 2))
            else:
                index = int((bomb.BASE_TIMEOUT - bomb.timeout) / self.RATE)
                self.select_sprite(0, index % 2)


class PlayerView(EntityView):
    PRIORITY = 20
    ROWS = 5
    COLUMNS = 8
    RATE = 0.1
    REMOVING_STEPS = [(4, 0), (4, 1), (4, 2)]

    direction_to_column = {
        None: 0,
        entity.Direction.DOWN: 0,
        entity.Direction.UP: 1,
        entity.Direction.RIGHT: 2,
        entity.Direction.LEFT: 3,
    }

    def __init__(self, entity_: entity.Player) -> None:
        self.FILE_NAME = f"player{entity_.identifier + 1}.png"  # pylint: disable = invalid-name
        super().__init__(entity_)

        i = self.direction_to_column[entity_.current_direction]
        self.select_sprite(i, 0)

    def notify(self, event_: event.Event) -> None:
        super().notify(event_)
        if event_.handled:
            return

        if isinstance(event_, events.MovedEntityEvent):
            player = cast(entity.Player, event_.entity)
            self.position = inflate_to_reality((player.position.i, player.position.j))
            if not player.current_direction:  # Player do not try to moves.
                self.select_sprite(self.direction_to_column[player.current_direction], 0) # Should refer to 0, 0
                return

            i = self.direction_to_column[player.current_direction]
            j = int(player.try_moving_since / self.RATE) % self.COLUMNS
            self.select_sprite(i, j)

            if player.next_position:
                next_position = inflate_to_reality((player.next_position.i, player.next_position.j))
                self.position = (
                    int((self.position[0] * (100 - player.step) + player.step * next_position[0]) / 100),
                    int((self.position[1] * (100 - player.step) + player.step * next_position[1]) / 100),
                )
