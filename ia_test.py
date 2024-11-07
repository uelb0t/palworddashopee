import sys
import math

GRID_SIZE = 5

# State from parameters
player = int(sys.argv[1]) 
enemy = 1 if player == 2 else 2 
board = sys.argv[2]
life1 = int(sys.argv[3])
life2 = int(sys.argv[4])
bullet1 = int(sys.argv[5])
bullet2 = int(sys.argv[6])

# Mounting matrix board
board = list(board)
res = []
for idx in range(0, len(board) // GRID_SIZE):
    res.append(board[idx * GRID_SIZE : (idx + 1) * GRID_SIZE])
board = [list(map(int, x)) for x in res]

# Getting player and enemy positions
pos_player = []
pos_enemy = []
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if board[i][j] == player:
            pos_player = [j,i]
        elif board[i][j] == enemy:
            pos_enemy = [j,i]

# If enemy is close, attack
if abs(pos_player[0] - pos_enemy[0]) <= 1 and abs(pos_player[1] - pos_enemy[1]) <= 1:
    print("attack")

# If not, move to the enemy
else:
    if pos_player[0] < pos_enemy[0]:
        print("right")
    elif pos_player[0] > pos_enemy[0]:
        print("left")
    elif pos_player[1] < pos_enemy[1]:
        print("down")
    else:
        print("up")
def minimax(board, depth, alpha, beta, maximizing_player, player, enemy):
          pos_player = []
          pos_enemy = []
          for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
              if board[i][j] == player:
                pos_player = [j, i]
              elif board[i][j] == enemy:
                pos_enemy = [j, i]

          if depth == 0 or (abs(pos_player[0] - pos_enemy[0]) <= 1 and abs(pos_player[1] - pos_enemy[1]) <= 1):
            return evaluate(board, player, enemy)

          if maximizing_player:
            max_eval = -math.inf
            for move in get_possible_moves(board, player):
              eval = minimax(move, depth - 1, alpha, beta, False, player, enemy)
              max_eval = max(max_eval, eval)
              alpha = max(alpha, eval)
              if beta <= alpha:
                break
            return max_eval
          else:
            min_eval = math.inf
            for move in get_possible_moves(board, enemy):
              eval = minimax(move, depth - 1, alpha, beta, True, player, enemy)
              min_eval = min(min_eval, eval)
              beta = min(beta, eval)
              if beta <= alpha:
                break
            return min_eval

def evaluate(board, player, enemy):
          pos_player = []
          pos_enemy = []
          for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
              if board[i][j] == player:
                pos_player = [j, i]
              elif board[i][j] == enemy:
                pos_enemy = [j, i]
          return -abs(pos_player[0] - pos_enemy[0]) - abs(pos_player[1] - pos_enemy[1])

def get_possible_moves(board, player):
          moves = []
          pos_player = []
          for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
              if board[i][j] == player:
                pos_player = [j, i]
          directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
          for direction in directions:
            new_pos = [pos_player[0] + direction[0], pos_player[1] + direction[1]]
            if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE and board[new_pos[1]][new_pos[0]] == 0:
              new_board = [row[:] for row in board]
              new_board[pos_player[1]][pos_player[0]] = 0
              new_board[new_pos[1]][new_pos[0]] = player
              moves.append(new_board)
          return moves

best_move = None
best_value = -math.inf
for move in get_possible_moves(board, player):
    move_value = minimax(move, 5, -math.inf, math.inf, False, player, enemy)
    if move_value > best_value:
      best_value = move_value
      best_move = move

print(best_move)