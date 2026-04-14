import os
from abc import ABC, abstractmethod

class ANSI:
    """Вспомогательный класс для хранения ANSI-кодов для форматирования вывода в консоль."""
    RESET = '\033[0m'
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'
    YELLOW_BG = '\033[43m'
    BLUE_BG = '\033[44m'
    CYAN_BG = '\033[46m'
    RED_TEXT = '\033[31m'
    GREEN_TEXT = '\033[32m'
    YELLOW_TEXT = '\033[33m'
    BLUE_TEXT = '\033[34m'
    WHITE_TEXT = '\033[97m'
    BLACK_TEXT = '\033[30m'

class Move:
    """Класс, описывающий шахматный ход и сохраняющий состояние для возможности отката."""
    def __init__(self, start_pos, end_pos, piece_moved, piece_captured, 
                 is_en_passant=False, en_passant_target_before=None, 
                 is_promotion=False, promoted_to=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.is_en_passant = is_en_passant
        self.en_passant_target_before = en_passant_target_before
        self.is_promotion = is_promotion
        self.promoted_to = promoted_to
        self.piece_moved_first_move_before = getattr(piece_moved, 'is_first_move', False)

class Piece(ABC):
    """Абстрактный базовый класс для всех шахматных фигур."""
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos
        self.symbol = '?'
        self.is_first_move = True

    @abstractmethod
    def get_pseudo_legal_moves(self, board):
        """Возвращает список возможных ходов фигуры без учета шаха собственному королю."""
        pass

    def get_sliding_moves(self, board, directions):
        """Вспомогательный метод для получения ходов дальнобойных фигур (Ладья, Слон, Ферзь)."""
        moves = []
        r, c = self.pos
        for dr, dc in directions:
            curr_r, curr_c = r + dr, c + dc
            while 0 <= curr_r < 8 and 0 <= curr_c < 8:
                target_piece = board.grid[curr_r][curr_c]
                if target_piece is None:
                    moves.append((curr_r, curr_c))
                elif target_piece.color != self.color:
                    moves.append((curr_r, curr_c))
                    break
                else:
                    break
                curr_r += dr
                curr_c += dc
        return moves

    def get_stepping_moves(self, board, moves_deltas):
        """Вспомогательный метод для получения ходов фигур с фиксированным шагом (Конь, Король)."""
        moves = []
        r, c = self.pos
        for dr, dc in moves_deltas:
            curr_r, curr_c = r + dr, c + dc
            if 0 <= curr_r < 8 and 0 <= curr_c < 8:
                target_piece = board.grid[curr_r][curr_c]
                if target_piece is None or target_piece.color != self.color:
                    moves.append((curr_r, curr_c))
        return moves

class Pawn(Piece):
    """Класс Пешки. Реализует ходы вперед, взятие по диагонали и взятие на проходе."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = '♙' if color == 'white' else '♟'

    def get_pseudo_legal_moves(self, board):
        """Определяет допустимые ходы пешки с учетом направления и специальных правил."""
        moves = []
        r, c = self.pos
        direction = -1 if self.color == 'white' else 1

        forward_r = r + direction
        if 0 <= forward_r < 8 and board.grid[forward_r][c] is None:
            moves.append((forward_r, c))
            if self.is_first_move:
                double_forward_r = r + 2 * direction
                if 0 <= double_forward_r < 8 and board.grid[double_forward_r][c] is None:
                    moves.append((double_forward_r, c))

        for dc in [-1, 1]:
            diag_c = c + dc
            if 0 <= forward_r < 8 and 0 <= diag_c < 8:
                target_piece = board.grid[forward_r][diag_c]
                if target_piece is not None and target_piece.color != self.color:
                    moves.append((forward_r, diag_c))
                elif board.en_passant_target == (forward_r, diag_c):
                    moves.append((forward_r, diag_c))
        return moves

class Rook(Piece):
    """Класс Ладьи."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = '♖' if color == 'white' else '♜'

    def get_pseudo_legal_moves(self, board):
        """Определяет ходы ладьи по вертикали и горизонтали."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.get_sliding_moves(board, directions)

class Knight(Piece):
    """Класс Коня."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = '♘' if color == 'white' else '♞'

    def get_pseudo_legal_moves(self, board):
        """Определяет Г-образные ходы коня."""
        moves_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                        (1, -2), (1, 2), (2, -1), (2, 1)]
        return self.get_stepping_moves(board, moves_deltas)

class Bishop(Piece):
    """Класс Слона."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = '♗' if color == 'white' else '♝'

    def get_pseudo_legal_moves(self, board):
        """Определяет диагональные ходы слона."""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.get_sliding_moves(board, directions)

class Queen(Piece):
    """Класс Ферзя."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = '♕' if color == 'white' else '♛'

    def get_pseudo_legal_moves(self, board):
        """Определяет ходы ферзя во всех направлениях."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.get_sliding_moves(board, directions)

class King(Piece):
    """Класс Короля."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = '♔' if color == 'white' else '♚'

    def get_pseudo_legal_moves(self, board):
        """Определяет ходы короля на одну клетку во всех направлениях."""
        moves_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                        (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.get_stepping_moves(board, moves_deltas)

class Chancellor(Piece):
    """Дополнительная фигура: Канцлер (объединяет ходы Ладьи и Коня)."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = 'C' if color == 'white' else 'c'

    def get_pseudo_legal_moves(self, board):
        """Определяет ходы канцлера."""
        knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                         (1, -2), (1, 2), (2, -1), (2, 1)]
        rook_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.get_stepping_moves(board, knight_deltas) + self.get_sliding_moves(board, rook_directions)

class Archbishop(Piece):
    """Дополнительная фигура: Архиепископ (объединяет ходы Слона и Коня)."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = 'A' if color == 'white' else 'a'

    def get_pseudo_legal_moves(self, board):
        """Определяет ходы архиепископа."""
        knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                         (1, -2), (1, 2), (2, -1), (2, 1)]
        bishop_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.get_stepping_moves(board, knight_deltas) + self.get_sliding_moves(board, bishop_directions)

class Amazon(Piece):
    """Дополнительная фигура: Амазонка (объединяет ходы Ферзя и Коня)."""
    def __init__(self, color, pos):
        super().__init__(color, pos)
        self.symbol = 'Z' if color == 'white' else 'z'

    def get_pseudo_legal_moves(self, board):
        """Определяет ходы амазонки."""
        knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), 
                         (1, -2), (1, 2), (2, -1), (2, 1)]
        queen_directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                            (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.get_stepping_moves(board, knight_deltas) + self.get_sliding_moves(board, queen_directions)

class Board:
    """Класс шахматной доски, управляющий матрицей клеток и валидацией состояния."""
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.move_log = []
        self.en_passant_target = None
        self.setup_standard_board()

    def place_piece(self, piece_class, color, r, c):
        """Размещает фигуру заданного класса и цвета на указанных координатах."""
        if 0 <= r < 8 and 0 <= c < 8:
            self.grid[r][c] = piece_class(color, (r, c))

    def setup_standard_board(self):
        """Инициализирует доску стандартной расстановкой шахматных фигур."""
        order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c in range(8):
            self.place_piece(Pawn, 'black', 1, c)
            self.place_piece(Pawn, 'white', 6, c)
            self.place_piece(order[c], 'black', 0, c)
            self.place_piece(order[c], 'white', 7, c)

    def get_valid_moves(self, piece):
        """Возвращает список ходов фигуры, отфильтрованный от ходов, оставляющих короля под шахом."""
        pseudo_moves = piece.get_pseudo_legal_moves(self)
        valid_moves = []
        for end_pos in pseudo_moves:
            if self.test_move_for_check(piece.pos, end_pos, piece.color):
                valid_moves.append(end_pos)
        return valid_moves

    def test_move_for_check(self, start_pos, end_pos, color):
        """Тестирует ход на виртуальной доске: безопасен ли он для короля текущего цвета."""
        sr, sc = start_pos
        er, ec = end_pos
        piece_to_move = self.grid[sr][sc]
        target_piece = self.grid[er][ec]
        
        self.grid[er][ec] = piece_to_move
        self.grid[sr][sc] = None
        piece_to_move.pos = (er, ec)
        
        is_safe = not self.is_in_check(color)
        
        self.grid[sr][sc] = piece_to_move
        self.grid[er][ec] = target_piece
        piece_to_move.pos = (sr, sc)
        
        return is_safe

    def is_in_check(self, color):
        """Проверяет, находится ли король указанного цвета под боем."""
        king_pos = None
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
                
        if not king_pos:
            return False
            
        enemy_color = 'black' if color == 'white' else 'white'
        return self.is_under_attack(king_pos[0], king_pos[1], enemy_color)

    def is_under_attack(self, r, c, attacker_color):
        """Проверяет, атакуется ли клетка хотя бы одной фигурой указанного цвета."""
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == attacker_color:
                    pseudo_moves = piece.get_pseudo_legal_moves(self)
                    if (r, c) in pseudo_moves:
                        return True
        return False

    def make_move(self, start_pos, end_pos, auto_promote_to=Queen):
        """Выполняет ход фигурой, обрабатывает специальные правила и записывает в историю."""
        sr, sc = start_pos
        er, ec = end_pos
        piece = self.grid[sr][sc]
        captured_piece = self.grid[er][ec]
        
        is_en_passant = False
        en_passant_target_before = self.en_passant_target
        is_promotion = False
        promoted_to = None

        if isinstance(piece, Pawn):
            if (er, ec) == self.en_passant_target:
                is_en_passant = True
                cap_r = sr
                cap_c = ec
                captured_piece = self.grid[cap_r][cap_c]
                self.grid[cap_r][cap_c] = None

            if abs(sr - er) == 2:
                self.en_passant_target = (sr + (-1 if piece.color == 'white' else 1), sc)
            else:
                self.en_passant_target = None

            if er == 0 or er == 7:
                is_promotion = True
                promoted_to = auto_promote_to
        else:
            self.en_passant_target = None

        move_record = Move(start_pos, end_pos, piece, captured_piece, 
                           is_en_passant, en_passant_target_before, 
                           is_promotion, promoted_to)
        
        self.grid[er][ec] = piece
        self.grid[sr][sc] = None
        piece.pos = (er, ec)
        piece.is_first_move = False

        if is_promotion and promoted_to:
            new_piece = promoted_to(piece.color, (er, ec))
            new_piece.is_first_move = False
            self.grid[er][ec] = new_piece

        self.move_log.append(move_record)

    def undo_move(self):
        """Откатывает последний сделанный ход, восстанавливая все состояния и срубленные фигуры."""
        if not self.move_log:
            return False
            
        move = self.move_log.pop()
        sr, sc = move.start_pos
        er, ec = move.end_pos

        piece_to_restore = move.piece_moved
        self.grid[sr][sc] = piece_to_restore
        piece_to_restore.pos = (sr, sc)
        piece_to_restore.is_first_move = move.piece_moved_first_move_before

        if move.is_promotion:
            self.grid[er][ec] = None
        else:
            self.grid[er][ec] = move.piece_captured
            if move.piece_captured and not move.is_en_passant:
                move.piece_captured.pos = (er, ec)

        if move.is_en_passant:
            cap_r = sr
            cap_c = ec
            self.grid[cap_r][cap_c] = move.piece_captured
            move.piece_captured.pos = (cap_r, cap_c)
            self.grid[er][ec] = None

        self.en_passant_target = move.en_passant_target_before
        return True

class Game:
    """Управляющий класс игрового цикла, взаимодействия с пользователем и консольного вывода."""
    def __init__(self):
        self.board = Board()
        self.turn = 'white'

    def toggle_turn(self):
        """Сменяет ход игрока."""
        self.turn = 'black' if self.turn == 'white' else 'white'

    def parse_position(self, pos_str):
        """Парсит строковые координаты вида 'e2' в индексы массива (r, c)."""
        if len(pos_str) != 2:
            return None
        col_str, row_str = pos_str[0].lower(), pos_str[1]
        if col_str < 'a' or col_str > 'h' or row_str < '1' or row_str > '8':
            return None
        col = ord(col_str) - ord('a')
        row = 8 - int(row_str)
        return (row, col)

    def format_position(self, r, c):
        """Форматирует индексы массива (r, c) в строковые координаты вида 'e2'."""
        return f"{chr(c + ord('a'))}{8 - r}"

    def print_board(self, hint_moves=None):
        """Отрисовывает шахматную доску в консоли с учетом угроз и подсветки ходов."""
        os.system('cls' if os.name == 'nt' else 'clear')
        enemy_color = 'black' if self.turn == 'white' else 'white'
        
        print("\n   a  b  c  d  e  f  g  h")
        print("  " + "-"*24)
        for r in range(8):
            row_str = f"{8 - r} |"
            for c in range(8):
                piece = self.board.grid[r][c]
                is_hint = hint_moves and (r, c) in hint_moves
                
                is_threatened = False
                if piece and piece.color == self.turn:
                    is_threatened = self.board.is_under_attack(r, c, enemy_color)

                bg_color = ""
                text_color = ""
                reset = ANSI.RESET

                if is_hint:
                    bg_color = ANSI.GREEN_BG
                    text_color = ANSI.BLACK_TEXT
                elif is_threatened:
                    bg_color = ANSI.RED_BG
                    text_color = ANSI.WHITE_TEXT
                else:
                    if piece:
                        text_color = ANSI.WHITE_TEXT if piece.color == 'white' else ANSI.YELLOW_TEXT

                symbol = piece.symbol if piece else ("*" if is_hint else ".")
                
                if bg_color or text_color:
                    row_str += f"{bg_color}{text_color} {symbol} {reset}"
                else:
                    row_str += f" {symbol} "
            row_str += f"| {8 - r}"
            print(row_str)
        print("  " + "-"*24)
        print("   a  b  c  d  e  f  g  h\n")

    def play(self):
        """Запускает основной цикл игры."""
        while True:
            self.print_board()
            if self.board.is_in_check(self.turn):
                print(f"{ANSI.RED_TEXT}ВНИМАНИЕ: {self.turn.upper()} КОРОЛЬ ПОД ШАХОМ!{ANSI.RESET}")

            print(f"Ход игрока: {self.turn.capitalize()}")
            print("Команды: 'e2 e4' (ход), 'hint e2' (подсказка), 'undo' (откат ходов), 'exit' (выход)")
            command = input("Ваш ввод: ").strip().lower()

            if command == 'exit':
                break
            
            if command == 'undo':
                if self.board.undo_move():
                    self.toggle_turn()
                else:
                    print("Нет ходов для отката.")
                    input("Нажмите Enter...")
                continue

            if command.startswith('hint '):
                parts = command.split()
                if len(parts) == 2:
                    pos = self.parse_position(parts[1])
                    if pos:
                        piece = self.board.grid[pos[0]][pos[1]]
                        if piece and piece.color == self.turn:
                            valid_moves = self.board.get_valid_moves(piece)
                            self.print_board(hint_moves=valid_moves)
                            print("Подсказка отображена.")
                            input("Нажмите Enter для продолжения...")
                        else:
                            print("На этой клетке нет вашей фигуры.")
                            input("Нажмите Enter...")
                continue

            parts = command.split()
            if len(parts) == 2:
                start_pos = self.parse_position(parts[0])
                end_pos = self.parse_position(parts[1])

                if not start_pos or not end_pos:
                    print("Неверный формат координат.")
                    input("Нажмите Enter...")
                    continue

                piece = self.board.grid[start_pos[0]][start_pos[1]]
                if not piece or piece.color != self.turn:
                    print("Вы не можете ходить этой фигурой.")
                    input("Нажмите Enter...")
                    continue

                valid_moves = self.board.get_valid_moves(piece)
                if end_pos not in valid_moves:
                    print("Недопустимый ход (возможно, нарушает правила или оставляет короля под шахом).")
                    input("Нажмите Enter...")
                    continue

                promoted_piece_class = Queen
                if isinstance(piece, Pawn) and (end_pos[0] == 0 or end_pos[0] == 7):
                    while True:
                        promo_input = input("Превращение пешки (q=Ферзь, r=Ладья, b=Слон, n=Коннь, c=Канцлер, a=Архиепископ, z=Амазонка) [q]: ").lower()
                        if promo_input == '' or promo_input == 'q': promoted_piece_class = Queen; break
                        elif promo_input == 'r': promoted_piece_class = Rook; break
                        elif promo_input == 'b': promoted_piece_class = Bishop; break
                        elif promo_input == 'n': promoted_piece_class = Knight; break
                        elif promo_input == 'c': promoted_piece_class = Chancellor; break
                        elif promo_input == 'a': promoted_piece_class = Archbishop; break
                        elif promo_input == 'z': promoted_piece_class = Amazon; break

                self.board.make_move(start_pos, end_pos, auto_promote_to=promoted_piece_class)
                self.toggle_turn()
            else:
                print("Неизвестная команда.")
                input("Нажмите Enter...")

if __name__ == "__main__":
    game = Game()
    game.play()
