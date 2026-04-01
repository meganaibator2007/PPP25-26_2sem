import copy # Библиотека для создания полных копий состояния доски (нужно для отката ходов)
import os # Инструменты ОС для включения цветного текста в консоли Windows

os.system("") # Активируем поддержку ANSI-цветов (в Windows 10/11 это включит цвета, в других ОС ничего не сломает)

# ==========================================
# 1. БАЗОВАЯ СУЩНОСТЬ: ФИГУРА
# ==========================================
class Piece: # Родительский класс для всех шахматных фигур
    def __init__(self, color, symbol): # Конструктор: срабатывает при создании любой фигуры
        self.color = color # Сохраняем цвет: 'w' (белые) или 'b' (черные)
        self.symbol = symbol # Сохраняем красивый символ Юникода для отрисовки
        self.has_moved = False # Флаг: ходила ли фигура (нужно для первого прыжка пешки)

    def slide(self, r, c, board, directions, max_steps=7): # Универсальный метод для "скользящих" фигур (Ладья, Слон, Ферзь)
        moves = [] # Пустой список для легальных ходов
        for dr, dc in directions: # Перебираем переданные направления (куда можно ехать)
            for step in range(1, max_steps + 1): # Едем по линии от 1 клетки до максимума
                nr, nc = r + dr * step, c + dc * step # Высчитываем координаты следующей клетки на линии
                if 0 <= nr < 8 and 0 <= nc < 8: # Если мы не улетели за края доски
                    target = board.grid[nr][nc] # Смотрим, кто стоит на этой клетке
                    if target is None: # Если клетка пустая
                        moves.append((nr, nc)) # Добавляем клетку в разрешенные ходы
                    elif target.color != self.color: # Если там стоит враг
                        moves.append((nr, nc)) # Можем его съесть (добавляем ход)
                        break # Но дальше ехать нельзя — линия перекрыта, стоп
                    else: # Если там стоит наша же фигура
                        break # Своих есть нельзя, перепрыгивать тоже, стоп
                else: # Если уперлись в край доски
                    break # Прерываем проверку этого направления
        return moves # Возвращаем все найденные ходы

    def get_moves(self, r, c, board): # Базовый метод получения ходов
        return [] # У абстрактной фигуры ходов нет, этот метод будут менять классы-наследники

# ==========================================
# 2. НАСЛЕДНИКИ: СТАНДАРТНЫЕ ФИГУРЫ
# ==========================================
class Pawn(Piece): # Пешка
    def __init__(self, color): # Конструктор пешки
        super().__init__(color, '♙' if color == 'w' else '♟') # Вызываем родителя, даем символ контурный или залитый
        self.direction = -1 if color == 'w' else 1 # Белые идут вверх по матрице (-1), черные вниз (+1)

    def get_moves(self, r, c, board): # Правила ходов пешки
        moves = [] # Список ходов
        nr = r + self.direction # Координата шага ровно вперед
        
        # 1. Движение вперед
        if 0 <= nr < 8 and board.grid[nr][c] is None: # Если впереди пусто
            moves.append((nr, c)) # Можем идти на 1 клетку
            if not self.has_moved: # Если пешка еще ни разу не ходила
                nnr = r + self.direction * 2 # Проверяем клетку через одну
                if board.grid[nnr][c] is None: # Если и там пусто
                    moves.append((nnr, c)) # Можем прыгнуть на 2 клетки сразу

        # 2. Обычное взятие по диагонали
        for dc in [-1, 1]: # Проверяем диагонали влево и вправо
            nc = c + dc # Соседняя колонка
            if 0 <= nc < 8 and 0 <= nr < 8: # Если не вышли за доску
                target = board.grid[nr][nc] # Смотрим, кто на диагонали
                if target and target.color != self.color: # Если там есть фигура и она чужая
                    moves.append((nr, nc)) # Можем срубить

        # 3. ДОП. ЗАДАНИЕ 8: Взятие на проходе (En Passant)
        if board.last_move: # Если в игре уже были ходы
            last_p, start, end = board.last_move # Смотрим, кто, откуда и куда ходил прямо перед нами
            if isinstance(last_p, Pawn) and abs(start[0] - end[0]) == 2: # Если это была пешка, сделавшая прыжок на 2 клетки
                if end[0] == r and abs(end[1] - c) == 1: # И если теперь она стоит ровно сбоку от нашей пешки
                    moves.append((nr, end[1])) # Разрешаем диагональный ход в пустую клетку ЗА вражеской пешкой
        return moves

class Knight(Piece): # Конь
    def __init__(self, color): super().__init__(color, '♘' if color == 'w' else '♞')
    def get_moves(self, r, c, board):
        moves = []
        for dr, dc in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]: # Все 8 прыжков буквой "Г"
            nr, nc = r + dr, c + dc # Координаты приземления
            if 0 <= nr < 8 and 0 <= nc < 8: # Если не за краем доски
                target = board.grid[nr][nc]
                if target is None or target.color != self.color: # Если клетка пустая или там враг
                    moves.append((nr, nc)) # Ход разрешен
        return moves

class Rook(Piece): # Ладья
    def __init__(self, color): super().__init__(color, '♖' if color == 'w' else '♜')
    def get_moves(self, r, c, board):
        return self.slide(r, c, board, [(0,1), (1,0), (0,-1), (-1,0)]) # Едет по 4 прямым направлениям

class Bishop(Piece): # Слон
    def __init__(self, color): super().__init__(color, '♗' if color == 'w' else '♝')
    def get_moves(self, r, c, board):
        return self.slide(r, c, board, [(1,1), (1,-1), (-1,1), (-1,-1)]) # Едет по 4 диагональным направлениям

class Queen(Piece): # Ферзь
    def __init__(self, color): super().__init__(color, '♕' if color == 'w' else '♛')
    def get_moves(self, r, c, board):
        return self.slide(r, c, board, [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]) # Едет во все 8 сторон

class King(Piece): # Король
    def __init__(self, color): super().__init__(color, '♔' if color == 'w' else '♚')
    def get_moves(self, r, c, board):
        return self.slide(r, c, board, [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)], 1) # Во все стороны, но максимум на 1 шаг

# ==========================================
# 3. ДОП. ЗАДАНИЕ 1: ТРИ НОВЫЕ ФИГУРЫ
# ==========================================
# Заменены названия фигур!
class RoyalGiant(Piece): # Королевский Гигант (Ладья + Конь)
    def __init__(self, color): super().__init__(color, 'R' if color == 'w' else 'r')
    def get_moves(self, r, c, board):
        moves = self.slide(r, c, board, [(0,1), (1,0), (0,-1), (-1,0)]) # Получаем ходы Ладьи
        moves.extend(Knight(self.color).get_moves(r, c, board)) # Прибавляем ходы Коня
        return moves

class ElixirGolem(Piece): # Элексирный голем (Слон + Конь)
    def __init__(self, color): super().__init__(color, 'E' if color == 'w' else 'e')
    def get_moves(self, r, c, board):
        moves = self.slide(r, c, board, [(1,1), (1,-1), (-1,1), (-1,-1)]) # Получаем ходы Слона
        moves.extend(Knight(self.color).get_moves(r, c, board)) # Прибавляем ходы Коня
        return moves

class MegaKnight(Piece): # Мегарыцарь (Прыгает ровно на 3 клетки в любую сторону сквозь фигуры)
    def __init__(self, color): super().__init__(color, 'M' if color == 'w' else 'm')
    def get_moves(self, r, c, board):
        moves = []
        for dr, dc in [(0,3), (3,0), (0,-3), (-3,0), (3,3), (3,-3), (-3,3), (-3,-3)]: # Фиксированные прыжки
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.grid[nr][nc]
                if target is None or target.color != self.color:
                    moves.append((nr, nc)) # Прыгает прямо на цель, игнорируя то, что стоит между ними
        return moves

# ==========================================
# 4. ОБЪЕКТ ДОСКИ И ИГРОВАЯ ЛОГИКА
# ==========================================
class Board: # Главный класс, управляющий матрицей игры
    def __init__(self):
        self.grid = [[None]*8 for _ in range(8)] # Создаем поле 8x8 из пустот (None)
        self.turn = 'w' # Чей сейчас ход (начинают белые)
        self.last_move = None # Информация о прошлом ходе для взятия на проходе
        self.history = [] # ДОП. ЗАДАНИЕ 5: Список для истории (откат)
        self.setup_board() # Вызываем расстановку

    def setup_board(self): # Расставляем фигуры на старте
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook] # Шаблон заднего ряда
        for c in range(8): # Проходим по всем колонкам
            self.grid[0][c] = back_rank[c]('b') # Расставляем черных
            self.grid[7][c] = back_rank[c]('w') # Расставляем белых
            self.grid[1][c] = Pawn('b') # Черные пешки
            self.grid[6][c] = Pawn('w') # Белые пешки
        
        # Заменяем некоторых коней и слонов на наши новые фигуры (Королевский Гигант, Элексирный голем, Мегарыцарь)
        self.grid[7][1] = RoyalGiant('w') 
        self.grid[7][6] = ElixirGolem('w') 
        self.grid[7][2] = MegaKnight('w') 
        self.grid[0][1] = RoyalGiant('b') 
        self.grid[0][6] = ElixirGolem('b') 
        self.grid[0][2] = MegaKnight('b')

    def print_board(self): # Отрисовка красивой цветной доски
        print("\n    a  b  c  d  e  f  g  h ") # Буквы сверху
        for r in range(8): # Идем по строкам
            row_str = f" {8 - r} " # Номер строки слева (от 8 до 1)
            for c in range(8): # Идем по клеткам
                p = self.grid[r][c] # Достаем фигуру
                
                # Чередуем цвета: четная сумма координат = светлая клетка, нечетная = темная
                if (r + c) % 2 == 0:
                    bg_color = "\033[47m" # ANSI-код: белый/светло-серый фон
                else:
                    bg_color = "\033[100m" # ANSI-код: темно-серый фон
                
                symbol = p.symbol if p else " " # Значок фигуры или пустота
                
                # Добавляем клетку (цвет, пробел, символ, пробел, сброс цвета \033[0m)
                row_str += f"{bg_color} {symbol} \033[0m"
                
            print(row_str + f" {8 - r}") # Выводим строку и номер справа
        print("    a  b  c  d  e  f  g  h \n") # Буквы снизу

    def is_in_check(self, color): # Проверка на Шах (угрозу королю)
        king_pos = None # Ищем короля
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if isinstance(p, King) and p.color == color: # Нашли нужного короля
                    king_pos = (r, c) # Запомнили координаты
        
        if not king_pos: return False # Защита, если короля нет

        for r in range(8): # Теперь смотрим всю доску
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color != color: # Находим все фигуры врага
                    if king_pos in p.get_moves(r, c, self): # Если король в их зоне поражения
                        return True # Значит, это Шах!
        return False

    def get_valid_moves(self, r, c): # Фильтрация ходов (нельзя ходить под шах)
        piece = self.grid[r][c] # Берем фигуру
        if not piece: return [] # Нет фигуры - нет ходов
        
        pseudo_moves = piece.get_moves(r, c, self) # Все теоретические ходы
        valid_moves = [] # Сюда сложим безопасные ходы
        
        for mr, mc in pseudo_moves: # Перебираем каждый ход
            target_piece = self.grid[mr][mc] # Запоминаем, кто там стоял
            
            # Сложная проверка для Взятия на проходе: чтобы не было "призрачной" пешки, которая дает ложный шах
            is_en_passant = isinstance(piece, Pawn) and mc != c and target_piece is None
            captured_ep = None
            if is_en_passant:
                captured_ep = self.grid[r][mc] # Сохраняем пешку врага
                self.grid[r][mc] = None # Временно удаляем ее с доски
                
            self.grid[mr][mc] = piece # Временно ставим нашу фигуру на новую клетку
            self.grid[r][c] = None # Убираем со старой
            
            if not self.is_in_check(piece.color): # Если после этого нет шаха нашему королю
                valid_moves.append((mr, mc)) # Значит ход легальный!
                
            # Возвращаем всю матрицу обратно как было
            self.grid[r][c] = piece 
            self.grid[mr][mc] = target_piece
            if is_en_passant:
                self.grid[r][mc] = captured_ep # Возвращаем съеденную пешку
                
        return valid_moves

    def get_all_valid_moves(self, color): # Собираем все ходы игрока (нужно для проверки мата)
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == color: # Находим все свои фигуры
                    moves.extend(self.get_valid_moves(r, c)) # Добавляем их разрешенные ходы в общий котел
        return moves

    def move_piece(self, start, end): # Метод совершения реального хода
        sr, sc = start # Координаты начала
        er, ec = end # Координаты конца
        piece = self.grid[sr][sc] # Фигура

        if not piece or piece.color != self.turn: # Если пусто или чужая фигура
            return False, "Не ваша фигура!"
            
        if end not in self.get_valid_moves(sr, sc): # Если ход нарушает правила
            return False, "Недопустимый ход!"

        # ДОП. ЗАДАНИЕ 5: Сохраняем полную копию всей доски перед ходом в историю (для отката)
        self.history.append({
            'grid': copy.deepcopy(self.grid), 
            'last_move': copy.deepcopy(self.last_move),
            'turn': self.turn
        })

        # ДОП. ЗАДАНИЕ 8: Удаляем пешку с доски при успешном взятии на проходе
        if isinstance(piece, Pawn) and ec != sc and self.grid[er][ec] is None:
            self.grid[sr][ec] = None 

        # ДОП. ЗАДАНИЕ 8: Превращение пешки в Ферзя, если дошла до конца
        if isinstance(piece, Pawn) and er in [0, 7]:
            piece = Queen(piece.color)

        self.grid[er][ec] = piece # Ставим на новое место
        self.grid[sr][sc] = None # Убираем со старого
        piece.has_moved = True # Отмечаем, что фигура ходила
        self.last_move = (piece, start, end) # Запоминаем этот ход для En Passant
        self.turn = 'b' if self.turn == 'w' else 'w' # Передаем ход сопернику
        return True, "Ход сделан."

    def undo(self): # ДОП. ЗАДАНИЕ 5: Откат хода
        if self.history: # Если в истории что-то есть
            state = self.history.pop() # Достаем последний сохраненный кадр
            self.grid = state['grid'] # Восстанавливаем расстановку
            self.last_move = state['last_move'] # Восстанавливаем прошлый ход
            self.turn = state['turn'] # Возвращаем очередь хода
            print(">>> Ход успешно отменен!")
        else:
            print(">>> Ошибка: Вы в самом начале партии, отменять нечего.")

    def show_threats(self): # ДОП. ЗАДАНИЕ 7: Показ фигур под угрозой
        threatened = [] # Список жертв
        for r in range(8): # Идем по доске
            for c in range(8):
                enemy = self.grid[r][c]
                if enemy and enemy.color != self.turn: # Находим врагов
                    for mr, mc in enemy.get_moves(r, c, self): # Смотрим, куда они бьют
                        friend = self.grid[mr][mc]
                        if friend and friend.color == self.turn: # Если там стоит наша фигура
                            coord = f"{chr(mc + 97)}{8 - mr}" # Переводим координаты в понятные (e4)
                            threatened.append(f"{friend.symbol} на {coord}") # Сохраняем в список
        if threatened:
            print(">>> ВНИМАНИЕ! Под ударом находятся:", ", ".join(set(threatened)))
        else:
            print(">>> Все ваши фигуры в безопасности.")

# ==========================================
# 5. ИНТЕРФЕЙС УПРАВЛЕНИЯ
# ==========================================
def play_game(): # Запуск игры
    board = Board()
    print("Добро пожаловать в ООП-Шахматы!")
    print("Новые фигуры: R (Королевский Гигант), E (Элексирный голем), M (Мегарыцарь).")
    print("Команды: 'e2 e4' (ход), 'undo' (откат), 'moves e2' (подсказка ходов), 'threats' (угрозы), 'quit' (выход).")

    while True: # Бесконечный цикл игры
        board.print_board() # Печатаем доску
        color_name = "БЕЛЫЕ" if board.turn == 'w' else "ЧЕРНЫЕ" # Имя текущего игрока
        
        all_moves = board.get_all_valid_moves(board.turn) # Собираем все легальные ходы игрока
        in_check = board.is_in_check(board.turn) # Проверяем, есть ли шах
        
        # Проверка конца игры (Мат или Пат)
        if not all_moves: # Если ходить некуда
            if in_check: # И при этом Шах
                print(f">>> ШАХ И МАТ! {color_name} проиграли.")
            else: # Шаха нет, но ходить некуда
                print(">>> ПАТ! Ничья.")
            break # Конец игры
            
        if in_check: # Просто предупреждение о шахе
            print(f">>> {color_name}, ВАШ КОРОЛЬ ПОД ШАХОМ!")

        command = input(f"Ход ({color_name}): ").strip().lower() # Ждем ввода команды

        if command == 'quit': # Выход
            break
        elif command == 'undo': # Команда отката
            board.undo()
        elif command == 'threats': # Команда показа угроз
            board.show_threats()
        elif command.startswith('moves'): # ДОП. ЗАДАНИЕ 6: Подсказка легальных ходов (moves e2)
            try:
                pos = command.split()[1] # Берем второе слово из команды
                c, r = ord(pos[0]) - 97, 8 - int(pos[1]) # Переводим букву в колонку, цифру в строку
                moves = board.get_valid_moves(r, c) # Просим доску дать безопасные ходы
                moves_str = [f"{chr(mc + 97)}{8 - mr}" for mr, mc in moves] # Переводим обратно в текст
                print(f">>> Доступные ходы: {', '.join(moves_str) if moves_str else 'нет допустимых ходов'}")
            except (IndexError, ValueError): # Защита от кривого ввода
                print(">>> Ошибка! Пишите так: moves e2")
        else: # Иначе считаем, что игрок ввел обычный ход (например: e2 e4)
            try:
                start_str, end_str = command.split() # Разбиваем на "откуда" и "куда"
                start = (8 - int(start_str[1]), ord(start_str[0]) - 97) # Декодируем старт
                end = (8 - int(end_str[1]), ord(end_str[0]) - 97) # Декодируем финиш
                
                success, message = board.move_piece(start, end) # Пытаемся сделать ход
                if not success: # Если ход не прошел проверку
                    print(">>> Ошибка:", message) # Пишем почему
            except (ValueError, IndexError): # Защита от опечаток типа "e2e4" без пробела
                print(">>> Неверный формат! Используйте: 'e2 e4'")
            except Exception as e: # Защита от падения программы
                print(f">>> Системная ошибка: {e}")

if __name__ == "__main__": # Точка входа в программу
    play_game() # Поехали!
