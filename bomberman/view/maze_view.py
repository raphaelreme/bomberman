"""Handle the Maze to display it on the screen."""

import pygame

from ..designpattern import event
from ..designpattern import observer
from ..model import events
from ..model import maze
from . import inflate_to_reality
from . import entity_view
from . import view


class MazeView(view.ImageView, observer.Observer):
    def __init__(self, maze_: maze.Maze) -> None:
        super().__init__(
            pygame.surface.Surface(inflate_to_reality(maze_.size)),  # pylint: disable = c-extension-no-member
            (0, 0),
        )

        self.maze = maze_
        self.maze.add_observer(self)

        # Select according to maze level ?
        self.style = 0
        background = view.load_image(f"bg{self.style + 1}.png", inflate_to_reality((1, 1)))

        for i in range(self.maze.size[0]):
            for j in range(self.maze.size[1]):
                self.image.blit(background, inflate_to_reality((i, j)))

        self.entity_views = {entity_view.EntityView.from_entity(entity_) for entity_ in self.maze.entities}

    def display(self) -> None:
        super().display()

        for view_ in sorted(self.entity_views):
            view_.display()

    def notify(self, event_: event.Event) -> None:
        if isinstance(event_, events.NewEntityEvent):
            self.entity_views.add(entity_view.EntityView.from_entity(event_.entity))
            event_.handled = True
            return
        if isinstance(event_, events.RemovedEntityEvent):
            for view_ in self.entity_views:
                if view_.entity == event_.entity:
                    self.entity_views.remove(view_)
                    break
