import os

import pygame

from .controller import control
from .controller import controller
from .model import maze
from .view import inflate_to_reality
from .view import maze_view
from .view import view


class Game:
    name = "Bomberman"
    @staticmethod
    def menu():
        return Game.game(input("Enter the level id: "))

    @staticmethod
    def game(maze_id):
        path = os.path.join(os.path.dirname(__file__), "data", "maze", f"{maze_id}.txt")
        maze_ = maze.Maze.read(path)

        pygame.display.set_mode(inflate_to_reality(maze_.size))
        pygame.display.set_caption(f"{Game.name} - level {maze_id}")
        pygame.display.set_icon(view.load_image("boom.png", (10, 10)))

        maze_view_ = maze_view.MazeView(maze_)
        main_controller = controller.GameController(maze_)

        running = True
        timer = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == control.TypeControl.QUIT:
                    running = False
                    break
                main_controller.handle_event(event)

            delta_time = timer.tick(48)/1000
            main_controller.time_spend(delta_time)

            maze_view_.display()
            pygame.display.flip()


def main():
    assert pygame.init() == (6, 0)  # pylint: disable = no-member
    Game.menu()
    pygame.quit()  # pylint: disable = no-member
