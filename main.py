# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pygame as pg
import ChessEngine
import Constants as C

pg.init()
pg.mixer.init()


"""
Initialize a dictionary of images in file Constants.
"""


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        C.IMAGES[piece] = pg.transform.scale(pg.image.load("assets/images1/" + piece + ".png"),
                                             (C.SQUARE_SIZE, C.SQUARE_SIZE))  # image takes whole square


# Sound effects
move_sound = pg.mixer.Sound("assets/sounds/move.mp3")
undo_sound = pg.mixer.Sound("assets/sounds/undo.mp3")
capture_sound = pg.mixer.Sound("assets/sounds/capture.mp3")
illegal_move_sound = pg.mixer.Sound("assets/sounds/illegal.mp3")
promotion_sound = pg.mixer.Sound("assets/sounds/promote.mp3")
check_sound = pg.mixer.Sound("assets/sounds/check-move.mp3")
castling_sound = pg.mixer.Sound("assets/sounds/castling.mp3")


"""
The main driver which handles user input and graphics updating.
"""


def main():
    # chess_window = pg.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    board_screen = pg.display.set_mode((C.BOARD_WIDTH, C.BOARD_HEIGHT))
    clock = pg.time.Clock()
    game_state = ChessEngine.Game()
    load_images()

    valid_moves = game_state.get_valid_moves()
    square_selected = ()
    player_clicks = []  # keep track of squares that the player clicked

    # flag variables
    move_made = False
    animate = False

    game_over = False
    run = True
    while run:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

            elif event.type == pg.MOUSEBUTTONDOWN:
                if not game_over:
                    location = pg.mouse.get_pos()
                    column = location[0] // C.SQUARE_SIZE
                    row = location[1] // C.SQUARE_SIZE

                    # user clicked the same square twice
                    if square_selected == (row, column):
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, column)
                        player_clicks.append(square_selected)  # appends 1st and 2nd clicks

                    # after 2nd click
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):

                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # reset user clicks
                                player_clicks = []
                                if valid_moves[i].is_pawn_promotion:
                                    pg.mixer.Sound.play(promotion_sound)
                                elif valid_moves[i].is_castling:
                                    pg.mixer.Sound.play(castling_sound)
                                elif valid_moves[i].piece_captured == "--":
                                    pg.mixer.Sound.play(move_sound)
                                else:
                                    pg.mixer.Sound.play(capture_sound)

                        if not move_made:
                            player_clicks = [square_selected]
                            #  pg.mixer.Sound.play(illegal_move_sound)
            # key handlers
            elif event.type == pg.KEYDOWN:
                # undo
                if event.key == pg.K_z:
                    game_state.undo()
                    move_made = True
                    animate = False
                    if game_over:
                        game_over = False
                    pg.mixer.Sound.play(undo_sound)
                # reset
                if event.key == pg.K_r:
                    game_state = ChessEngine.Game()
                    valid_moves = game_state.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False

        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], board_screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False
        draw_game_state(board_screen, game_state, valid_moves, square_selected)

        # Game end
        if game_state.check_mate:
            game_over = True
            if game_state.white_turn:
                draw_text(board_screen, "Black wins")
            else:
                draw_text(board_screen, "White wins")
        elif game_state.stale_mate:
            game_over = True
            draw_text(board_screen, "Stalemate")

        clock.tick(C.FPS)
        pg.display.flip()

    pg.quit()


"""
Highlight square selected and moves available for that piece
"""


def highlight_possible_squares(board_screen, game_state, valid_moves, square_selected):
    if square_selected != ():
        row, column = square_selected
        if game_state.board[row][column][0] == ('w' if game_state.white_turn else 'b'):
            surface = pg.Surface((C.SQUARE_SIZE, C.SQUARE_SIZE))
            surface.set_alpha(C.TRANSPARENCY)
            surface.fill(pg.Color('blue'))
            board_screen.blit(surface, (column * C.SQUARE_SIZE, row * C.SQUARE_SIZE))

            surface.fill(pg.Color("yellow"))
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    board_screen.blit(surface, (C.SQUARE_SIZE * move.end_column, C.SQUARE_SIZE * move.end_row))


"""
Highlight the last move made
"""


def highlight_last_move(board_screen, move):
    pass


"""
Graphics handler for the current game state.
"""


def draw_game_state(board_screen, game_state, valid_moves, square_selected):
    draw_board(board_screen)
    highlight_possible_squares(board_screen, game_state, valid_moves, square_selected)
    draw_pieces(board_screen, game_state.board)


"""
Draw the squares on the board.
"""


def draw_board(board_screen):
    global colors
    colors = [pg.Color("light gray"), pg.Color("dark gray")]
    for row in range(C.DIMENSION):
        for column in range(C.DIMENSION):
            if row % 2 == 0:
                if column % 2 == 0:
                    # draw white
                    pg.draw.rect(board_screen, colors[0], [column * C.SQUARE_SIZE, row * C.SQUARE_SIZE,
                                                           C.SQUARE_SIZE, C.SQUARE_SIZE])
                else:
                    # draw black
                    pg.draw.rect(board_screen, colors[1], [column * C.SQUARE_SIZE, row * C.SQUARE_SIZE,
                                                           C.SQUARE_SIZE, C.SQUARE_SIZE])
            else:
                if column % 2 == 0:
                    # draw black
                    pg.draw.rect(board_screen, colors[1], [column * C.SQUARE_SIZE, row * C.SQUARE_SIZE,
                                                           C.SQUARE_SIZE, C.SQUARE_SIZE])
                else:
                    # draw white
                    pg.draw.rect(board_screen, colors[0], [column * C.SQUARE_SIZE, row * C.SQUARE_SIZE,
                                                           C.SQUARE_SIZE, C.SQUARE_SIZE])


"""
Draw the pieces on the board using the current Game.board
"""


def draw_pieces(board_screen, board):
    for row in range(C.DIMENSION):
        for column in range(C.DIMENSION):
            piece = board[row][column]
            if piece != "--":
                board_screen.blit(C.IMAGES[piece], pg.Rect(column * C.SQUARE_SIZE, row * C.SQUARE_SIZE,
                                                           C.SQUARE_SIZE, C.SQUARE_SIZE))


"""
Animating a move
"""


def animate_move(move, board_screen, board, clock):
    global colors
    delta_row = move.end_row - move.start_row
    delta_column = move.end_column - move.start_column
    frames_per_square = 5
    frame_count = (abs(delta_row) + abs(delta_column)) * frames_per_square
    for frame in range(frame_count + 1):
        row, column = ((move.start_row + delta_row * frame/frame_count,
                       move.start_column + delta_column * frame/frame_count))
        draw_board(board_screen)
        draw_pieces(board_screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_column) % 2]
        end_square = pg.Rect(move.end_column * C.SQUARE_SIZE, move.end_row * C.SQUARE_SIZE,
                             C.SQUARE_SIZE, C.SQUARE_SIZE)
        pg.draw.rect(board_screen, color, end_square)

        # draw captured piece onto the rectangle
        if move.piece_captured != "--" and not move.is_en_passant:
            board_screen.blit(C.IMAGES[move.piece_captured], end_square)
        # draw moving piece
        board_screen.blit(C.IMAGES[move.piece_moved], pg.Rect(column * C.SQUARE_SIZE, row * C.SQUARE_SIZE,
                                                              C.SQUARE_SIZE, C.SQUARE_SIZE))
        pg.display.flip()
        clock.tick(C.FPS)


def draw_text(board_screen, text):
    font = pg.font.SysFont("Adobe Arabic", 64, True, False)
    text_object = font.render(text, 0, pg.Color('purple'))
    text_location = pg.Rect(0, 0, C.BOARD_WIDTH, C.BOARD_HEIGHT)\
        .move(C.BOARD_WIDTH/2 - text_object.get_width()/2, C.BOARD_HEIGHT/2 - text_object.get_height()/2)
    board_screen.blit(text_object, text_location)


if __name__ == "__main__":
    main()
