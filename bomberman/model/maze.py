"""Main part of the model: class Maze.

It holds all the data of the game.
"""

from __future__ import annotations

from typing import Optional, Set, Tuple

from ..designpattern import observable
from . import entity
from . import events



class MazeException(Exception):
    pass


class OutOfMazeError(MazeException):
    pass


class MazeDescriptionError(MazeException):
    pass


class Maze(observable.Observable):
    """Contains all the entities of the game.

    The maze can be observed in order to know which object it contains.

    Attrs:
        size (Tuple[int, int]): Number of boxes of the maze. (row, columns)
        entities (List[Entity]): All the entity in the maze.
    """
    SEP = "|"
    VOID = " "

    def __init__(self, size: Tuple[int, int]) -> None:
        super().__init__()
        self.size = size
        self.entities: Set[entity.Entity] = set()

    def add_entity(self, entity_: entity.Entity) -> None:
        if not self.is_inside(entity_.position):
            raise OutOfMazeError(f"Try to add {entity_} at {entity_.position}. Out of boundaries: {self.size}")

        self.entities.add(entity_)
        self.changed(events.NewEntityEvent(entity_))

    def remove_entity(self, entity_: entity.Entity) -> None:
        self.entities.remove(entity_)
        self.changed(events.RemovedEntityEvent(entity_))

    def contains(self, entity_classes: Tuple[entity.EntityClass, ...], position: entity.Position) -> bool:
        for entity_ in self.entities:
            if entity_.position == position and isinstance(entity_, entity_classes):
                return True
        return False

    def is_inside(self, position: entity.Position) -> bool:
        return 0 <= position.i < self.size[0] and 0 <= position.j < self.size[1]

    def get_player_count(self) -> int:
        return len(list(filter(lambda entity_: isinstance(entity_, entity.Player), self.entities)))

    def __str__(self) -> str:
        tmp = [
            [Maze.VOID for _ in range(self.size[1])] for _ in range(self.size[0])
        ]
        for entity_ in self.entities:
            if not hasattr(entity_, "REPR"):
                continue
            i, j = entity_.position.i, entity_.position.j
            tmp[i][j] = getattr(entity_, "REPR")

        return "\n".join(map(Maze.SEP.join, tmp))

    def serialize(self) -> str:
        return str(self)

    @staticmethod
    def unserialize(string: str) -> Maze:
        lines = string.strip().split("\n")
        matrix = list(map(lambda line: line.split(Maze.SEP), lines))

        rows = len(matrix)
        columns = len(matrix[0])
        maze = Maze((rows, columns))

        for i, line in enumerate(matrix):
            if len(line) != columns:
                raise MazeDescriptionError(f"Line {i} has not the same shape as the first line.")

            for j, char in enumerate(line):
                if char == Maze.VOID:
                    continue
                klass: Optional[entity.EntityClass] = entity.EntityClass.representation_to_entity_class.get(char)

                if not klass:
                    raise MazeDescriptionError(f"Unkown identifier: '{char}' at {(i, j)}")

                maze.entities.add(klass(maze, entity.Position(i, j)))

        return maze

    def save(self, file_name: str) -> None:
        with open(file_name, "w") as file:
            file.write(self.serialize())

    @staticmethod
    def read(file_name: str) -> Maze:
        with open(file_name, "r") as file:
            return Maze.unserialize(file.read())
