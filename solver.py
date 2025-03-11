import numpy as np
import random
from collections import deque
from config import SIZE

class Solver:
    def __init__(self, board):
        self.board = board
        self.size = len(board)

    def is_valid(self, r, c, color):
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            return False  # Out of bounds
        if self.board[r, c] != 2:
            return False  # Already filled

        # Simulate placing the color
        self.board[r, c] = color
        valid = self.is_fully_connected()
        self.board[r, c] = 2  # Revert move

        if not valid:
            print(f"Rejected move: ({r}, {c}) for color {color}")
        return valid

    def is_fully_connected(self):
        def bfs(start_r, start_c, color):
            queue = deque([(start_r, start_c)])
            visited = set([(start_r, start_c)])
            while queue:
                r, c = queue.popleft()
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < SIZE and 0 <= nc < SIZE and
                            self.board[nr, nc] == color and (nr, nc) not in visited):
                        visited.add((nr, nc))
                        queue.append((nr, nc))
            return visited

        black_start = white_start = None
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r, c] == 0 and black_start is None:
                    black_start = (r, c)
                if self.board[r, c] == 1 and white_start is None:
                    white_start = (r, c)

        if not black_start or not white_start:
            return False

        black_connected = bfs(*black_start, 0)
        white_connected = bfs(*white_start, 1)
        total_black = sum(1 for row in self.board for cell in row if cell == 0)
        total_white = sum(1 for row in self.board for cell in row if cell == 1)

        if len(black_connected) != total_black:
            print("❌ Black cells are not fully connected!")
        if len(white_connected) != total_white:
            print("❌ White cells are not fully connected!")
        
        return len(black_connected) == total_black and len(white_connected) == total_white

    def is_solved(self):
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r, c] == 2:
                    return False  # Còn ô trống, chưa giải xong
        return self.is_fully_connected()  # Kiểm tra kết nối đầy đủ

    def bfs_solve(self):
        black_queue = deque()
        white_queue = deque()

        # Khởi tạo hàng đợi từ vị trí đã có màu
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r, c] == 0:
                    black_queue.append((r, c))
                elif self.board[r, c] == 1:
                    white_queue.append((r, c))

        preferred_directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while black_queue or white_queue:
            if self.is_solved():  # ✅ Nếu đã giải xong, thoát
                print("Puzzle solved successfully! 🎉")
                return self.board

            next_black = deque()
            next_white = deque()

            # 🔹 Xử lý ô đen
            for _ in range(len(black_queue)):  # Lặp đúng số lượng phần tử hiện có
                r, c = black_queue.popleft()
                for dr, dc in preferred_directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr, nc] == 2:
                        if self.is_valid(nr, nc, 0):  # ✅ Nếu hợp lệ, đặt màu luôn
                            self.board[nr, nc] = 0
                            next_black.append((nr, nc))
                        else:
                            black_queue.append((r, c))  # ❌ Không hợp lệ, đẩy lại hàng đợi

            # 🔹 Xử lý ô trắng
            for _ in range(len(white_queue)):
                r, c = white_queue.popleft()
                for dr, dc in preferred_directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr, nc] == 2:
                        if self.is_valid(nr, nc, 1):  # ✅ Nếu hợp lệ, đặt màu luôn
                            self.board[nr, nc] = 1
                            next_white.append((nr, nc))
                        else:
                            white_queue.append((r, c))  # ❌ Không hợp lệ, đẩy lại hàng đợi

            # Cập nhật hàng đợi cho bước tiếp theo
            black_queue = next_black
            white_queue = next_white

        return self.board
