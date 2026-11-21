import pygame
from loader import Loader
from input_handler import InputHandler
from renderer import Renderer
from board import Board
from ai import AiEngine


def main():
    """Run the Pygame Chess game loop.

    Contract:
    - Inputs: None (takes 0 arguments; polls events via pygame.event.get()).
    - Returns: None.
    - Loop Domain & Behavior:
        - Line 10: Initializes pygame via pygame.init().
        - Line 11: Creates a 720x720 display surface.
        - Line 18: Performs initial board draw via renderer.draw(screen).
        - Line 21: Enters main event loop while running == True:
            - pygame.QUIT (line 25): Sets running = False to terminate loop.
            - pygame.MOUSEBUTTONDOWN (line 28): If not board.game_over(),
              dispatches mouse position to input_handler, then triggers
              ai.computer_move() if game remains active.
            - Other events (KEYDOWN, MOUSEMOTION, etc.): Ignored.
            - Frame update (line 37): Invokes renderer.draw(screen) on each loop iteration.
            - Game over (line 39): If board.game_over() is True, waits 5000ms
              via pygame.time.wait(5000) and sets running = False.
    - Mutation: Mutates board state through legal moves and AI responses; does not mutate
      any external caller arguments.
    """
    pygame.init()
    screen = pygame.display.set_mode((720, 720))
    loader = Loader()

    board = Board()
    input_handler = InputHandler(board)
    ai = AiEngine(board)
    renderer = Renderer(input_handler, board, loader)
    renderer.draw(screen)

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if not board.game_over():

                    input_handler.get_mouse_pos()

                    if not board.game_over():
                        ai.computer_move()

        renderer.draw(screen)

        if board.game_over():
            pygame.time.wait(5000)
            running = False


if __name__ == "__main__":
    main()
