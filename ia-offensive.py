import math
import sys
from copy import deepcopy

GRID_SIZE = 5
INF = math.inf

# State from parameters
PLAYER = int(sys.argv[1]) 
ENEMY = 1 if PLAYER == 2 else 2 
BOARD = sys.argv[2]
player_life = int(sys.argv[3])
enemy_life = int(sys.argv[4])
PLAYER_AMMO = int(sys.argv[5])
ENEMY_AMMO = int(sys.argv[6])

# Mounting matrix board
BOARD = list(BOARD)
res = []
for idx in range(0, len(BOARD) // GRID_SIZE):
    res.append(BOARD[idx * GRID_SIZE : (idx + 1) * GRID_SIZE])
board = [list(map(int, x)) for x in res]

def get_board_data(board, player, enemy):
  pos_player = []
  pos_enemy = []
  pos_weapon = []
  pos_heart = []
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if board[i][j] == player:
            pos_player = [j,i]
        elif board[i][j] == enemy:
            pos_enemy = [j,i]
        elif board[i][j] == 3:
            pos_weapon = [j,i]
        elif board[i][j] == 4:
            pos_heart = [j,i]

  return pos_player, pos_enemy, pos_weapon, pos_heart

def evaluate(board, player, enemy):
    pos_player, pos_enemy, pos_weapon, pos_heart = get_board_data(board, player, enemy)
    score = 0

    player_heart_distance = abs(pos_player[0] - pos_heart[0]) + abs(pos_player[1] - pos_heart[1])
    player_weapon_distance = abs(pos_player[0] - pos_weapon[0]) + abs(pos_player[1] - pos_weapon[1])
    enemy_heart_distance = abs(pos_enemy[0] - pos_heart[0]) + abs(pos_enemy[1] - pos_heart[1])
    enemy_weapon_distance = abs(pos_enemy[0] - pos_weapon[0]) + abs(pos_enemy[1] - pos_weapon[1])

    if player_life <= enemy_life and player_heart_distance <= 1:
        score += 100
    if PLAYER_AMMO > (enemy_life + 1) and enemy_heart_distance >= 2:
        score += 500
    if enemy_life > player_life and enemy_heart_distance <= 1:
        score -= 100
    if ENEMY_AMMO > (player_life + 1) and player_heart_distance >= 2:
        score -= 500

    score += player_heart_distance + player_weapon_distance - (enemy_heart_distance * 0.5) - (enemy_weapon_distance * 0.5)
    return score

def endgame():
    if player_life <= 0 or enemy_life <= 0:
        return True
    return False

def in_diagonals(pos1, pos2):
    if abs(pos1[0] - pos2[0]) == 1 and abs(pos1[1] - pos2[1]) == 1:
        return True
    return False

def all_possible_actions(board, pos_player, pos_enemy):
    actions = []
    possible_moves = [(0, -1, "left"), (0, 1, "right"), (-1, 0, "up"), (1, 0, "down")]
    print(board, pos_player, pos_enemy)

    for move in possible_moves:
        new_x = pos_player[0] + move[0]
        new_y = pos_player[1] + move[1]
        print("new xy", [new_x, new_y], move[2])
        if new_x >= 0 and new_x < len(board) and new_y >= 0 and new_y < len(board[0]) and (board[new_y][new_x] == 0 or board[new_y][new_x] == 4 or board[new_y][new_x] == 3):
            actions.append(move[2])

    if (abs(pos_player[0] - pos_enemy[0]) + abs(pos_player[1] - pos_enemy[1]) == 1) or in_diagonals(pos_player, pos_enemy):
        actions.append("attack")
        actions.append("block")

    print("actions", actions)

    return actions
        

def minimax(board, depth, isMaximizing, alpha, beta):
    player = PLAYER if isMaximizing else ENEMY
    enemy = ENEMY if isMaximizing else PLAYER
    if depth == 0 or endgame():
        return (None, evaluate(board, player, enemy))
    
    pos_player, pos_enemy, _, _ = get_board_data(board, player, enemy)
    print('depth', depth, 'player', player)
    print('minimax', pos_player, pos_enemy)
    if isMaximizing:
        best_move = None
        maxEval = -INF
        for action in all_possible_actions(board, pos_player, pos_enemy):
            if action == "left":
                new_x = pos_player[0] - 1
                new_y = pos_player[1]
            elif action == "right":
                new_x = pos_player[0] + 1
                new_y = pos_player[1]
            elif action == "up":
                new_x = pos_player[0]
                new_y = pos_player[1] - 1
            elif action == "down":
                new_x = pos_player[0]
                new_y = pos_player[1] + 1
            elif action == "attack":
                if player == 1:
                    enemy_life -= 1
                else:
                    player_life -= 1

            new_board = deepcopy(board)
            new_board[new_y][new_x] = player
            new_board[pos_player[1]][pos_player[0]] = 0
            evaluation = minimax(new_board, depth - 1, False, alpha, beta)[1]
            maxEval = max(maxEval, evaluation)
            alpha = max(alpha, evaluation)
            if maxEval == evaluation:
                best_move = action
            if beta <= alpha:
                break
            
        return best_move, maxEval
    else:
        minEval = INF
        for action in all_possible_actions(board, pos_enemy, pos_player):
            if action == "left":
                new_x = pos_enemy[0] - 1
                new_y = pos_enemy[1]
            elif action == "right":
                new_x = pos_enemy[0] + 1
                new_y = pos_enemy[1]
            elif action == "up":
                new_x = pos_enemy[0]
                new_y = pos_enemy[1] - 1
            elif action == "down":
                new_x = pos_enemy[0]
                new_y = pos_enemy[1] + 1

            new_board = deepcopy(board)
            new_board[new_y][new_x] = enemy
            new_board[pos_enemy[1]][pos_enemy[0]] = 0
            evaluation = minimax(new_board, depth - 1, True, alpha, beta)[1]
            minEval = min(minEval, evaluation)
            beta = min(beta, evaluation)
            if minEval == evaluation:
                best_move = action
            if beta <= alpha:
                break

        return best_move, minEval
    
def get_best_move(board):
    best_move, score = minimax(board, 3, True, -INF, INF)

    print("score", score, "best_move", best_move)
    
    return "block"

get_best_move(board)