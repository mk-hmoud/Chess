import copy


class Game:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]

        ]
        self.move_log = []
        self.white_turn = True
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False
        self.player_is_in_check = False
        self.pins = []
        self.checks = []
        self.en_passant_valid_square = ()
        self.current_castling_rights = Castling(True, True, True, True)
        self.castling_rights_log = [Castling(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                             self.current_castling_rights.bks, self.current_castling_rights.bqs)]

    """
    Execute a Move object
    """
    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved

        #  update kings location if moved
        if move.piece_moved[1] == "K":
            if move.piece_moved[0] == "w":
                self.white_king_location = (move.end_row, move.end_column)
            else:
                self.black_king_location = (move.end_row, move.end_column)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + 'Q'

        #  en-passant
        self.en_passant_valid_square = ()
        if move.piece_moved[1] == 'P':
            if abs(move.end_row - move.start_row) == 2:
                self.en_passant_valid_square = (move.end_row + 1, move.end_column) \
                                                if move.piece_moved[0] == 'w' \
                                                else (move.end_row - 1, move.end_column)
        if move.is_en_passant:
            if self.white_turn:
                self.board[move.end_row + 1][move.end_column] = "--"
            else:
                self.board[move.end_row - 1][move.end_column] = "--"

        # castling
        if move.is_castling:
            if move.end_column - move.start_column == 2:  # king side castle
                self.board[move.end_row][move.end_column - 1] = self.board[move.end_row][move.end_column + 1]
                self.board[move.end_row][move.end_column + 1] = "--"
            else:  # Queen side castle
                self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 2]
                self.board[move.end_row][move.end_column - 2] = "--"

        self.move_log.append(move)  # log the move to undo later, or display history of moves
        self.white_turn = not self.white_turn  # switch turns

        self.update_castling(move)
        self.castling_rights_log.append(Castling(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                                 self.current_castling_rights.bks, self.current_castling_rights.bqs))

    """
    Undo last move
    """
    def undo(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            if move.is_en_passant:
                if move.piece_moved[0] == 'w':
                    self.board[move.end_row + 1][move.end_column] = move.piece_captured
                else:
                    self.board[move.end_row - 1][move.end_column] = move.piece_captured
                self.board[move.end_row][move.end_column] = "--"
                self.en_passant_valid_square = (move.end_row, move.end_column)

            else:
                self.board[move.end_row][move.end_column] = move.piece_captured

            self.board[move.start_row][move.start_column] = move.piece_moved
            self.white_turn = not self.white_turn

            #  update kings location if undone
            if move.piece_moved[1] == "K":
                if move.piece_moved[0] == "w":
                    self.white_king_location = (move.start_row, move.start_column)
                else:
                    self.black_king_location = (move.start_row, move.start_column)

            if move.is_pawn_promotion:
                self.board[move.start_row][move.start_column] = self.board[move.start_row][move.start_column][0] + 'P'

            self.castling_rights_log.pop()
            castle_rights = copy.deepcopy(self.castling_rights_log[-1])
            self.current_castling_rights = castle_rights
            if move.is_castling:
                if move.end_column - move.start_column == 2:  # king side castle
                    self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 1]
                    self.board[move.end_row][move.end_column - 1] = "--"
                else:  # Queen side castle
                    self.board[move.end_row][move.end_column - 2] = self.board[move.end_row][move.end_column + 1]
                    self.board[move.end_row][move.end_column + 1] = "--"

            if self.check_mate:
                self.check_mate = False
            elif self.stale_mate:
                self.stale_mate = False

    def update_castling(self, move):
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved[1] == 'R':

            if move.piece_moved[0] == 'w' and move.start_row == 7:
                if move.start_column == 0:  # left Rook
                    self.current_castling_rights.wqs = False
                elif move.start_column == 7:  # right Rook
                    self.current_castling_rights.wks = False

            elif move.piece_moved[0] == 'b' and move.start_row == 0:
                if move.start_column == 0:  # left Rook
                    self.current_castling_rights.bqs = False
                elif move.start_column == 7:  # right Rook
                    self.current_castling_rights.bks = False

        # if a rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_column == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_column == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_column == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_column == 7:
                    self.current_castling_rights.bks = False

    """
    All moves considering checks
    """
    def get_valid_moves(self):
        valid_moves = []
        self.player_is_in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_turn:
            king_row = self.white_king_location[0]
            king_column = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_column = self.black_king_location[1]
        if self.player_is_in_check:
            if len(self.checks) == 1:
                valid_moves = self.get_possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_column = check[1]
                piece_checking = self.board[check_row][check_column]
                valid_squares = []
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_column)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_column + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_column:
                            break
                for i in range(len(valid_moves) - 1, -1, -1):
                    if valid_moves[i].piece_moved[1] != 'K':
                        if not (valid_moves[i].end_row, valid_moves[i].end_column) in valid_squares:
                            valid_moves.remove(valid_moves[i])
            else:
                self.get_king_moves(king_row, king_column, valid_moves)
        else:
            valid_moves = self.get_possible_moves()

        for move in valid_moves:
            print(str(move))

        if len(valid_moves) == 0 and self.player_is_in_check:
            self.check_mate = True
        elif len(valid_moves) == 0 and not self.player_is_in_check:
            self.stale_mate = True

        return valid_moves

    def check_for_pins_and_checks(self, row=-1, column=-1):
        pins = []
        checks = []
        in_check = False
        if self.white_turn:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_column = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_column = self.black_king_location[1]
        if not row == column == -1:
            start_row = row
            start_column = column

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            d = directions[i]
            possible_pin = ()
            for j in range(1, 8):
                end_row = start_row + d[0] * j
                end_column = start_column + d[1] * j
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    end_piece = self.board[end_row][end_column]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            possible_pin = (end_row, end_column, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        if(0 <= i <= 3 and piece_type == 'R') or \
                                (4 <= i <= 7 and piece_type == 'B') or \
                                (j == 1 and piece_type == 'P' and ((enemy_color == 'w' and 6 <= i <= 7) or (enemy_color == 'b' and 4 <= i <= 5))) or \
                                (piece_type == 'Q') or (j == 1 and piece_type == 'K'):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_column, d[0], d[1]))
                                break
                            else:  # piece blocking so pin it
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying check
                            break

        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)]

        for move in knight_moves:
            end_row = start_row + move[0]
            end_column = start_column + move[1]

            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_column, move[0], move[1]))
        return in_check, pins, checks

    """
    All moves without considering checks
    """
    def get_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                piece_color = self.board[row][column][0]
                piece_type = self.board[row][column][1]
                if (piece_color == 'w' and self.white_turn) or (piece_color == 'b' and not self.white_turn):
                    self.move_functions[piece_type](row, column, moves)  # calls the appropriate move function depending
                                                                        # on the piece type
        return moves

    """
    Get all the pawn moves for the pawn located at row, column and add these moves to the list
    """
    def get_pawn_moves(self, row, column, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_turn:
            if row > 0:
                if self.board[row - 1][column] == "--":  # 1 square pawn move
                    if not piece_pinned or pin_direction == (-1, 0):
                        moves.append(Move((row, column), (row - 1, column), self.board))
                        if row == 6 and self.board[row - 2][column] == "--":  # 2 square pawn move
                            moves.append(Move((row, column), (row - 2, column), self.board))

                    # capture enemy pawn moves
                if column - 1 >= 0:
                    if self.board[row - 1][column - 1][0] == 'b':
                        if not piece_pinned or pin_direction == (-1, -1):
                            moves.append(Move((row, column), (row - 1, column - 1), self.board))
                if column + 1 <= 7:
                    if self.board[row - 1][column + 1][0] == 'b':
                        if not piece_pinned or pin_direction == (-1, 1):
                            moves.append(Move((row, column), (row - 1, column + 1), self.board))

        else:  # black pawn moves
            if row < 7:
                if self.board[row + 1][column] == "--":  # 1 square pawn move
                    if not piece_pinned or pin_direction == (1, 0):
                        moves.append(Move((row, column), (row + 1, column), self.board))
                        if row == 1 and self.board[row + 2][column] == "--":  # 2 square pawn move
                            moves.append(Move((row, column), (row + 2, column), self.board))

                # capture enemy pawn moves
                if column - 1 >= 0:
                    if self.board[row + 1][column - 1][0] == 'w':
                        if not piece_pinned or pin_direction == (1, -1):
                            moves.append(Move((row, column), (row + 1, column - 1), self.board))
                if column + 1 <= 7:
                    if self.board[row + 1][column + 1][0] == 'w':
                        if not piece_pinned or pin_direction == (1, 1):
                            moves.append(Move((row, column), (row + 1, column + 1), self.board))
        # en passant
        if not self.en_passant_valid_square == ():
            if abs(column - self.en_passant_valid_square[1]) == 1:

                if self.white_turn and row == self.en_passant_valid_square[0] + 1:
                    move = Move((row, column), self.en_passant_valid_square, self.board)
                    move.is_en_passant = True
                    move.piece_captured = self.board[move.end_row + 1][move.end_column]
                    moves.append(move)

                elif not self.white_turn and row == self.en_passant_valid_square[0] - 1:
                    move = Move((row, column), self.en_passant_valid_square, self.board)
                    move.is_en_passant = True
                    move.piece_captured = self.board[move.end_row - 1][move.end_column]
                    moves.append(move)

    """
    Get all the pawn moves for the rook located at row, column and add these moves to the list
    """

    def get_rook_moves(self, row, column, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][column][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # N, W, S, E
        enemy_color = 'b' if self.white_turn else 'w'

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = column + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:  # Check bounds
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # Empty space
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # Capture enemy piece
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                            break
                        else:  # Friendly piece
                            break
                else:  # Out of bounds
                    break
        #  self.castling(row, column, moves)

    """
    Get all the pawn moves for the knight located at row, column and these moves to the list
    """

    def get_knight_moves(self, row, column, moves):

        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)]

        ally_color = 'w' if self.white_turn else 'b'

        for move in knight_moves:
            end_row = row + move[0]
            end_col = column + move[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((row, column), (end_row, end_col), self.board))

    """
    Get all the pawn moves for the bishop located at row, column and these moves to the list
    """

    def get_bishop_moves(self, row, column, moves):

        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][column][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, 1), (-1, -1), (1, 1), (1, -1)]  # NE, NW, SE, SW
        enemy_color = 'b' if self.white_turn else 'w'

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = column + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:  # Check bounds
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # Empty space
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # Capture enemy piece
                            moves.append(Move((row, column), (end_row, end_col), self.board))
                            break
                        else:  # Friendly piece
                            break
                else:  # Out of bounds
                    break

    """
    Get all the queen moves for the pawn located at row, column and these moves to the list
    """

    def get_queen_moves(self, row, column, moves):
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)

    """
    Get all the king moves for the pawn located at row, column and these moves to the list
    """

    def get_king_moves(self, row, column, moves):
        row_moves    = (-1, -1, -1,  0, 0,  1, 1, 1)
        column_moves = (-1,  0,  1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.white_turn else 'b'
        for i in range(8):
            end_row = row + row_moves[i]
            end_column = column + column_moves[i]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                if end_piece[0] != ally_color:
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_column)
                    else:
                        self.black_king_location = (end_row, end_column)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, column), (end_row, end_column), self.board))

                    if ally_color == 'w':
                        self.white_king_location = (row, column)
                    else:
                        self.black_king_location = (row, column)
        self.get_castling_moves(row, column, moves)

    def get_castling_moves(self, row, column, moves):
        if self.player_is_in_check:
            return
        if (self.white_turn and self.current_castling_rights.wks) or \
                (not self.white_turn and self.current_castling_rights.bks):
            self.get_king_side_castling_moves(row, column, moves)

        if (self.white_turn and self.current_castling_rights.wqs) or \
                (not self.white_turn and self.current_castling_rights.bqs):
            self.get_queen_side_castling_moves(row, column, moves)

    def get_king_side_castling_moves(self, row, column, moves):
        if self.board[row][column + 1] == self.board[row][column + 2] == "--":
            in_check1, pins1, checks1 = self.check_for_pins_and_checks(row, column + 1)
            in_check2, pins2, checks2 = self.check_for_pins_and_checks(row, column + 2)
            if not in_check1 and not in_check2:
                moves.append(Move((row, column), (row, column + 2), self.board, is_castling=True))

    def get_queen_side_castling_moves(self, row, column, moves):
        if self.board[row][column - 1] == self.board[row][column - 2] == self.board[row][column - 3] == "--":
            in_check1, pins1, checks1 = self.check_for_pins_and_checks(row, column - 1)
            in_check2, pins2, checks2 = self.check_for_pins_and_checks(row, column - 2)
            if not in_check1 and not in_check2:
                moves.append(Move((row, column), (row, column - 2), self.board, is_castling=True))


class Castling:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move:

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_columns = {"a": 0, "b": 1, "c": 2, "d": 3,
                        "e": 4, "f": 5, "g": 6, "h": 7}
    columns_to_files = {v: k for k, v in files_to_columns.items()}

    def __init__(self, start_square, end_square, board, is_castling=False):
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        self.is_en_passant = False
        self.is_castling = is_castling
        self.is_pawn_promotion = ((self.piece_moved == "wP" and self.end_row == 0)
                                  or
                                  (self.piece_moved == "bP" and self.end_row == 7))
        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def __str__(self):
        return f'Move piece: {self.piece_moved} from ({self.start_row}, {self.start_column})' \
               f' to ' \
               f'({self.end_row}, {self.end_column})'

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]
