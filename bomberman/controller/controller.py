"""Controllers of the game.

Handle all the events.
"""

from __future__ import annotations

from typing import List

import pygame

from ..model import entity
from ..model import maze
from . import control


class GameController:
    def __init__(self, maze_: maze.Maze):
        self.maze: maze.Maze = maze_
        self.controllers = []

        for entity_ in self.maze.entities:
            if isinstance(entity_, entity.Player):
                self.controllers.append(PlayerController(entity_))
            if isinstance(entity_, entity.Enemy):
                pass

    def handle_event(self, event) -> bool:
        """Handle all the graphical events.

        Args:
            event (pygame.event.Event): The event received.

        Returns:
            bool: True if the event has been handled. False otherwise.
        """
        # if event.type == control.TypeControl.KEY_DOWN and event.key == control.BaseControl.RETURN:
        #     try:
        #         player_ = self.maze.new_player()
        #     except maze.MazeFullError:
        #         return False
        #     self.players.append(PlayerController(player_))
        #     return True

        for controller in self.controllers:
            if controller.handle_event(event):
                return True
        return False

    def time_spend(self, delta_time: float) -> None:
        for entity_ in self.maze.entities.copy():
            entity_.update(delta_time)
        for controller in self.controllers:
            controller.time_spend(delta_time)


class PlayerController:
    def __init__(self, player: entity.Player) -> None:
        self.player = player
        self.player_control = control.PlayerControl.from_identifier(self.player.identifier)
        self.key_to_direction = {
            self.player_control.up: entity.Direction.UP,
            self.player_control.down: entity.Direction.DOWN,
            self.player_control.right: entity.Direction.RIGHT,
            self.player_control.left: entity.Direction.LEFT,
        }
        self.direction_pressed: List[int] = []
        self.bombing = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event for the player concerned.

        Args:
            event (pygame.event.Event): The event received.

        Returns:
            bool: True if the event has been handled. False otherwise.
        """
        if event.type not in (control.TypeControl.KEY_DOWN, control.TypeControl.KEY_UP):
            return False

        if event.key == self.player_control.bombs:
            self.bombing = (event.type == control.TypeControl.KEY_DOWN)
            return True

        if event.key not in self.key_to_direction:
            return False

        if event.type == control.TypeControl.KEY_DOWN:
            assert event.key not in self.direction_pressed
            self.direction_pressed.append(event.key)
        elif event.type == control.TypeControl.KEY_UP:
            self.direction_pressed.remove(event.key)

        if not self.direction_pressed:
            self.player.set_wanted_direction(None)
        else:
            self.player.set_wanted_direction(self.key_to_direction[self.direction_pressed[-1]])

        return True

    def time_spend(self, delta_time: float):
        if self.bombing:
            self.player.bombs()
