"""Provides the basic class for simple views."""

from __future__ import annotations

import os
from typing import List, Tuple

import pygame


def load_image(file_name: str, size: Tuple[int, int] = None) -> pygame.SurfaceType:  # pylint: disable = no-member
    """Load an image from the image folder (bomberman/data/image).

    Should only be called when the main window (mode) has been set.

    Args:
        file_name (str)
        size (Optional): Convert the image to this size. (in pixels)

    Return:
        pygame.Surface: The image loaded.
    """
    real_location = os.path.join(os.path.dirname(__file__), '..', 'data', 'image', file_name)

    if size:
        return pygame.transform.scale(pygame.image.load(real_location).convert_alpha(), size)
    return pygame.image.load(real_location).convert_alpha()


class ImageView:
    """Class for views based on an image.

    It can be displayed on the main_window, but you have to open a window first.

    Attrs:
        window (pygame.Surface): The pygame surface on which the image
            will be displayed.
        image (pygame.Surface): The pygame surface to display.
        position (Tuple[int, int]): Positions of the image on the window.
    """

    def __init__(self, image: pygame.Surface, position: Tuple[int, int]) -> None:  # pylint: disable = no-member
        # pylint does not find the pygame.Surface class.
        self.window: pygame.Surface = pygame.display.get_surface()  # pylint: disable = no-member
        self.image = image
        self.position = position

    def display(self) -> None:
        self.window.blit(self.image, self.position)


class Sprite(ImageView):
    """Handle a sprite image to animated a view

    Attr:
        SPRITE_SIZE (Tuple[int, int]): Size of all the sprites. (Same size)
        ROWS (int): Number of sprite rows in the image.
        COLUMNS (int): Number of sprite columns in the image.
    """
    SPRITE_SIZE = (32, 32)
    ROWS = 1
    COLUMNS = 1

    def __init__(self, image: pygame.Surface, position: Tuple[int, int]) -> None:  # pylint: disable = no-member
        super().__init__(image, position)
        self.rect = pygame.Rect((0, 0), self.SPRITE_SIZE)

    def select_sprite(self, row: int, column: int) -> None:
        assert row < self.ROWS and column < self.COLUMNS
        self.rect = pygame.Rect((column * self.SPRITE_SIZE[0], row * self.SPRITE_SIZE[1]), self.SPRITE_SIZE)

    def display(self) -> None:
        self.window.blit(self.image, self.position, self.rect)
