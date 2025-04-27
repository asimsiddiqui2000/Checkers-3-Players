import tkinter as tk
import random

# Constants
RED = 'R'
BLUE = 'B'
GREEN = 'G'
EMPTY = '.'
BOARD_SIZE = 15
CELL_SIZE = 40

class CheckersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("3-Player Checkers")
        self.canvas = tk.Canvas(root, width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE)
        self.canvas.pack()

        self.board = self.init_board()
        self.players = [RED, BLUE, GREEN]
        self.turn = 0
        self.selected = None

        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.root.after(1000, self.bot_move_if_needed)

    def init_board(self):
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for r in range(13, 15):
            for c in range(3):
                board[r][c] = RED
        for r in range(13, 15):
            for c in range(12, 15):
                board[r][c] = BLUE
        for r in range(2):
            for c in range(6, 9):
                board[r][c] = GREEN
        return board

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                fill_color = "lightgreen" if self.selected == (r, c) else "beige"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)

                piece = self.board[r][c]
                if piece != EMPTY:
                    color = {RED: "red", BLUE: "blue", GREEN: "green"}[piece]
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill=color)

    def get_valid_moves(self, player):
        directions = {
            RED: [(-1, -1), (-1, 1)],
            BLUE: [(-1, -1), (-1, 1)],
            GREEN: [(1, -1), (1, 1)]
        }
        enemy_players = [p for p in self.players if p != player]
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    for dr, dc in directions[player]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                            if self.board[nr][nc] == EMPTY:
                                moves.append(((r, c), (nr, nc)))
                            elif self.board[nr][nc] in enemy_players:
                                jr, jc = nr + dr, nc + dc
                                if 0 <= jr < BOARD_SIZE and 0 <= jc < BOARD_SIZE and self.board[jr][jc] == EMPTY:
                                    moves.append(((r, c), (jr, jc)))
        return moves

    def make_move(self, move):
        (sr, sc), (er, ec) = move
        piece = self.board[sr][sc]
        self.board[sr][sc] = EMPTY
        captured = None
        if abs(sr - er) == 2:
            mr, mc = (sr + er) // 2, (sc + ec) // 2
            captured = self.board[mr][mc]
            self.board[mr][mc] = EMPTY
        self.board[er][ec] = piece
        self.draw_board()
        return captured

    def handle_click(self, event):
        player = self.players[self.turn % 3]
        if player == GREEN:
            return

        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE

        if self.selected:
            start = self.selected
            end = (r, c)
            valid_moves = self.get_valid_moves(player)
            if (start, end) in valid_moves:
                self.make_move((start, end))
                self.selected = None
                self.turn += 1
                self.root.after(500, self.bot_move_if_needed)
            else:
                self.selected = None
            self.draw_board()
        elif self.board[r][c] == player:
            self.selected = (r, c)
            self.draw_board()

    def evaluate_board(self):
        return sum(cell == GREEN for row in self.board for cell in row)

    def minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.evaluate_board(), None

        player = GREEN if maximizing else RED
        moves = self.get_valid_moves(player)
        best_move = None

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                captured = self.make_move(move)
                eval_score, _ = self.minimax(board, depth-1, alpha, beta, False)
                self.undo_move(move, GREEN, captured)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                captured = self.make_move(move)
                eval_score, _ = self.minimax(board, depth-1, alpha, beta, True)
                self.undo_move(move, RED, captured)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def undo_move(self, move, player, captured=None):
        (sr, sc), (er, ec) = move
        self.board[sr][sc] = player
        if abs(sr - er) == 2 and captured:
            mr, mc = (sr + er) // 2, (sc + ec) // 2
            self.board[mr][mc] = captured
        self.board[er][ec] = EMPTY
        self.draw_board()

    def bot_move_if_needed(self):
        if self.players[self.turn % 3] == GREEN:
            _, move = self.minimax(self.board, 2, float('-inf'), float('inf'), True)
            if move:
                self.make_move(move)
            self.turn += 1
        self.check_winner()

    def check_winner(self):
        alive = set(cell for row in self.board for cell in row if cell in [RED, BLUE, GREEN])
        if len(alive) == 1:
            winner = alive.pop()
            self.canvas.create_text(
                BOARD_SIZE * CELL_SIZE // 2,
                BOARD_SIZE * CELL_SIZE // 2,
                text=f"Game Over! {winner} wins!",
                fill="black",
                font=("Arial", 24)
            )

if __name__ == '__main__':
    root = tk.Tk()
    game = CheckersGUI(root)
    root.mainloop()
