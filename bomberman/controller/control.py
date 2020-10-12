"""Defines all the control key for the game"""

from __future__ import annotations

import json
import enum
import os

from pygame import locals as p_locals


class TypeControl(enum.IntEnum):
    QUIT = p_locals.QUIT  # pylint: disable = no-member
    KEY_DOWN = p_locals.KEYDOWN  # pylint: disable = no-member
    KEY_UP = p_locals.KEYUP  # pylint: disable = no-member


class BaseControl(enum.IntEnum):
    ESCAPE = p_locals.K_ESCAPE  # pylint: disable = no-member
    RETURN = p_locals.K_RETURN  # pylint: disable = no-member


class PlayerControl:
    DEFAULT_UP = p_locals.K_UP  # pylint: disable = no-member
    DEFAULT_DOWN = p_locals.K_DOWN  # pylint: disable = no-member
    DEFAULT_RIGHT = p_locals.K_RIGHT  # pylint: disable = no-member
    DEFAULT_LEFT = p_locals.K_LEFT  # pylint: disable = no-member
    DEFAULT_BOMBS = p_locals.K_SPACE  # pylint: disable = no-member

    def __init__(self, identifier: int):
        self.identifier = identifier
        self.up = self.DEFAULT_UP  # pylint: disable = invalid-name
        self.down = self.DEFAULT_DOWN
        self.right = self.DEFAULT_RIGHT
        self.left = self.DEFAULT_LEFT
        self.bombs = self.DEFAULT_BOMBS

    def serialize(self) -> str:
        return json.dumps({
            "up": self.up,
            "down": self.down,
            "right": self.right,
            "left": self.left,
            "bombs": self.bombs,
        })

    @staticmethod
    def unserialize(string: str, identifier: int) -> PlayerControl:
        json_object = json.loads(string)

        control = PlayerControl(identifier)
        control.up = json_object["up"]
        control.down = json_object["down"]
        control.right = json_object["right"]
        control.left = json_object["left"]
        control.bombs = json_object["bombs"]

        return control

    def save(self) -> None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "control", f"player{self.identifier}.txt")
        with open(path, "w") as file:
            file.write(str(self))

    @staticmethod
    def from_identifier(identifier: int) -> PlayerControl:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "control", f"player{identifier}.txt")
        if not os.path.exists(path):
            return PlayerControl(identifier)

        with open(path, "r") as file:
            return PlayerControl.unserialize(file.read(), identifier)
