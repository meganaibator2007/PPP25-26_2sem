import copy

class Piece:
    def __init__(self, color, name, char):
        self.color = color
        self.name = name
        self.char = char

    def get_legal_moves(self, board, x, y, history):
        return []

class MegaKnight(Piece):
    def get_legal_moves(self, board, x, y, history):
        moves = []
        offsets = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1),
                   (0,2),(0,-2),(2,0),(-2,0)]
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves

class Witch(Piece):
    def get_legal_moves(self, board, x, y, history):
        moves = []
        for dx, dy in [(-1,-1), (1,-1), (-1,1), (1,1)]:
            for i in range(1, 4):
                nx, ny = x + dx*i, y + dy*i
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = board[ny][nx]
                    if target is None or target.color != self.color:
                        moves.append((nx, ny))
        return moves

class Valkyrie(Piece):
    def get_legal_moves(self, board, x, y, history):
        moves = []
        offsets = [(0,1),(0,-1),(1,0),(-1,0), (0,2),(0,-2),(2,0),(-2,0),
                   (1,1),(1,-1),(-1,1),(-1,-1)]
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                target = board[ny][nx]
                if target is None or target.color != self.color:
                    moves.append((nx, ny))
        return moves

class Pawn(Piece):
    def get_legal_moves(self, board, x, y, history):
        moves = []
        dir = -1 if self.color == 'W' else 1
        if 0 <= y+dir < 8 and board[y+dir][x] is None:
            moves.append((x, y+dir))
            if (y == 6 and self.color == 'W') or (y == 1 and self.color == 'B'):
                if board[y+dir*2][x] is None: moves.append((x, y+dir*2))
        for dx in [-1, 1]:
            nx, ny = x + dx, y + dir
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[ny][nx] and board[ny][nx].color != self.color: moves.append((nx, ny))
                if history:
                    last = history[-1]
                    if isinstance(last['p'], Pawn) and last['t'] == (nx, y) and abs(last['f'][1] - last['t'][1]) == 2:
                        moves.append((nx, ny))
        return moves

class King(Piece):
    def get_legal_moves(self, board, x, y, history):
        moves = []
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx == 0 and dy == 0: continue
                nx, ny = x+dx, y+dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    if board[ny][nx] is None or board[ny][nx].color != self.color: moves.append((nx, ny))
        return moves

class SlidingPiece(Piece):
    def __init__(self, color, name, char, dirs):
        super().__init__(color, name, char)
        self.dirs = dirs

    def get_legal_moves(self, board, x, y, history):
        moves = []
        for dx, dy in self.dirs:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board[ny][nx] is None:
                    moves.append((nx, ny))
                elif board[ny][nx].color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves

class ChessEngine:
    def __init__(self):
        self.grid = [[None]*8 for _ in range(8)]
        self.history = []
        self.turn = 'W'
        self.prepare_board()

    def prepare_board(self):
        rooks = [lambda c: SlidingPiece(c, 'Rook', 'R', [(0,1),(0,-1),(1,0),(-1,0)]),
                 lambda c: MegaKnight(c, 'MegaKnight', 'M'),
                 lambda c: Witch(c, 'Witch', 'W'),
                 lambda c: SlidingPiece(c, 'Queen', 'Q', [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]),
                 lambda c: King(c, 'King', 'K'),
                 lambda c: Valkyrie(c, 'Valkyrie', 'V'),
                 lambda c: SlidingPiece(c, 'Bishop', 'B', [(1,1),(1,-1),(-1,1),(-1,-1)]),
                 lambda c: SlidingPiece(c, 'Rook', 'R', [(0,1),(0,-1),(1,0),(-1,0)])]
        
        for i in range(8):
            self.grid[0][i] = rooks[i]('B')
            self.grid[1][i] = Pawn('B', 'Pawn', 'p')
            self.grid[6][i] = Pawn('W', 'Pawn', 'P')
            self.grid[7][i] = rooks[i]('W')

    def in_check(self, board, color):
        kx, ky = -1, -1
        for y in range(8):
            for x in range(8):
                if isinstance(board[y][x], King) and board[y][x].color == color:
                    kx, ky = x, y
        for y in range(8):
            for x in range(8):
                p = board[y][x]
                if p and p.color != color:
                    if (kx, ky) in p.get_legal_moves(board, x, y, self.history): return True
        return False

    def get_filtered_moves(self, x, y):
        p = self.grid[y][x]
        if not p or p.color != self.turn: return []
        raw_moves = p.get_legal_moves(self.grid, x, y, self.history)
        safe_moves = []
        for mx, my in raw_moves:
            temp = copy.deepcopy(self.grid)
            temp[my][mx] = temp[y][x]
            temp[y][x] = None
            if not self.in_check(temp, self.turn): safe_moves.append((mx, my))
        return safe_moves

    def execute_move(self, x1, y1, x2, y2):
        if (x2, y2) not in self.get_filtered_moves(x1, y1): return False
        p = self.grid[y1][x1]
        self.history.append({'g': copy.deepcopy(self.grid), 'f':(x1,y1), 't':(x2,y2), 'p':p, 'turn':self.turn})
        
        if isinstance(p, Pawn) and x1 != x2 and self.grid[y2][x2] is None: self.grid[y1][x2] = None
        
        self.grid[y2][x2], self.grid[y1][x1] = p, None
        
        if isinstance(p, Pawn) and y2 in [0, 7]:
            self.grid[y2][x2] = SlidingPiece(p.color, 'Queen', 'Q' if p.color=='W' else 'q', [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)])
            
        self.turn = 'B' if self.turn == 'W' else 'W'
        return True

    def undo(self):
        if self.history:
            old = self.history.pop()
            self.grid, self.turn = old['g'], old['turn']

    def render(self, h_pos=None):
        print("\n    0  1  2  3  4  5  6  7")
        hints = self.get_filtered_moves(*h_pos) if h_pos else []
        threats = []
        for y in range(8):
            for x in range(8):
                p = self.grid[y][x]
                if p and p.color != self.turn: threats.extend(p.get_legal_moves(self.grid, x, y, self.history))

        for y in range(8):
            line = f" {y} "
            for x in range(8):
                p = self.grid[y][x]
                bg = "\033[42m" if (x+y)%2==0 else "\033[40m"
                fg = "\033[97m" if p and p.color == 'W' else "\033[91m"
                reset = "\033[0m"
                
                char = p.char if p else " "
                if (x, y) in hints: char = f"({char})"
                elif p and p.color == self.turn and (x, y) in threats: char = f"*{char}*"
                else: char = f" {char} "
                
                line += f"{bg}{fg}{char}{reset}"
            print(line)

if __name__ == "__main__":
    game = ChessEngine()
    print("=" * 45)
    print("  ИНТЕРАКТИВНЫЙ ШАХМАТНЫЙ ДВИЖОК v2.0")
    print("=" * 45)
    print(" Доступные команды:")
    print(" - Перемещение: x_откуда y_откуда x_куда y_куда")
    print(" - Подсветка:   show x y")
    print(" - Отмена хода: back")
    print("=" * 45)

    while True:
        game.render()
        current_player = "БЕЛЫЕ" if game.turn == 'W' else "ЧЕРНЫЕ"
        
        try:
            inp = input(f"\n[Очередь: {current_player}] Введите команду > ").split()
            if not inp:
                continue
                
            if inp[0] == 'back':
                game.undo()
                print(">> Последний ход успешно отменен.")
                
            elif inp[0] == 'show' and len(inp) == 3:
                game.render((int(inp[1]), int(inp[2])))
                
            elif len(inp) == 4:
                if not game.execute_move(int(inp[0]), int(inp[1]), int(inp[2]), int(inp[3])):
                    print(">> [ОШИБКА] Нелегальный ход или угроза королю!")
            else:
                print(">> [ОШИБКА] Неизвестная команда. Повторите ввод.")
                
        except KeyboardInterrupt:
            print("\n>> Завершение работы движка. До свидания!")
            break
        except Exception:
            print(">> [ОШИБКА] Неверный формат ввода! Используйте цифры.")
