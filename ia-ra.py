import sys
import math
from copy import deepcopy

GRID_SIZE = 5
INF = math.inf

# State from parameters
player = int(sys.argv[1]) 
enemy = 1 if player == 2 else 2 
board_arg = sys.argv[2]
life1 = int(sys.argv[3])
life2 = int(sys.argv[4])
bullet1 = int(sys.argv[5])
bullet2 = int(sys.argv[6])

# Mounting matrix board
def mount_board(board):
  board = list(board)
  res = []
  for idx in range(0, len(board) // GRID_SIZE):
      res.append(board[idx * GRID_SIZE : (idx + 1) * GRID_SIZE])
  board = [list(map(int, x)) for x in res]
  
  return board

# Getting player and enemy positions
def get_board_positions(board, player, enemy):
  pos_player = []
  pos_enemy = []
  pos_gun = []
  pos_heart = []
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if board[i][j] == player:
            pos_player = [j,i]
        elif board[i][j] == enemy:
            pos_enemy = [j,i]
        elif board[i][j] == 3:
            pos_gun = [j,i]
        elif board[i][j] == 4:
            pos_heart = [j,i]
            
  return pos_player, pos_enemy, pos_gun, pos_heart
            
def is_on_diagonals(pos1, pos2):
  if abs(pos1[0] - pos2[0]) == 1 and abs(pos1[1] - pos2[1]) == 1:
    return True
  return False            

def all_possible_actions(board, player, enemy):
    actions = []
    pos_player, pos_enemy, _, _ = get_board_positions(board, player, enemy)
    movements = [(-1, 0, "up"), (1, 0, "down"), (0, 1, "right"), (0, -1, "left")]
    for move in movements:
      new_pos = [pos_player[0] + move[0], pos_player[1] + move[1]]
      if new_pos[0] >= 0 and new_pos[0] < GRID_SIZE and new_pos[1] >= 0 and new_pos[1] < GRID_SIZE and board[new_pos[1]][new_pos[0]] == 0 or board[new_pos[1]][new_pos[0]] == 3 or board[new_pos[1]][new_pos[0]] == 4:
        actions.append(move[2])
            
    if abs(pos_player[0] - pos_enemy[0]) <= 1 and abs(pos_player[1] - pos_enemy[1]) <= 1 or is_on_diagonals(pos_player, pos_enemy):
        actions.append("attack")
        actions.append("block")
        
    return actions
   
def decode_state(state):
  player = int(state[0])
  enemy = 2 if player == 1 else 1
  board_config = state[1]
  player_life = int(state[2])
  enemy_life = int(state[3])
  player_ammo = int(state[4])
  enemy_ammo = int(state[5])
  player_is_blocking = False
  enemy_is_blocking = False
  
  board = mount_board(board_config)
   
  return {
      "player": player,
      "enemy": enemy,
      "board": board,
      "player_life": player_life,
      "enemy_life": enemy_life,
      "player_ammo": player_ammo,
      "enemy_ammo": enemy_ammo,
      "player_is_blocking": player_is_blocking,
      "enemy_is_blocking": enemy_is_blocking
  }
  
def create_state_string(player, board, player_life, enemy_life, player_ammo, enemy_ammo):
  return [str(player)] + [''.join(str(item) for item in board)] + [str(player_life)] + [str(enemy_life)] + [str(player_ammo)] + [str(enemy_ammo)]
    
def mount_state(state, action, is_string):
  state = decode_state(state) if is_string else state
  print("old_state", state, "action", action)
  new_state = deepcopy(state)
  pos_player, _, _, _ = get_board_positions(new_state["board"], new_state["player"], new_state["enemy"])
  if action == "up":
    new_state["board"][pos_player[1]][pos_player[0]] = 0
    new_state["board"][pos_player[1] - 1][pos_player[0]] = state["player"]
  elif action == "down":
    new_state["board"][pos_player[1]][pos_player[0]] = 0
    new_state["board"][pos_player[1] + 1][pos_player[0]] = state["player"]
  elif action == "left":
    new_state["board"][pos_player[1]][pos_player[0]] = 0
    new_state["board"][pos_player[1]][pos_player[0] - 1] = state["player"]
  elif action == "right":
    new_state["board"][pos_player[1]][pos_player[0]] = 0
    new_state["board"][pos_player[1]][pos_player[0] + 1] = state["player"]
  elif action == "attack":
    damage = 1
    if new_state["player_ammo"] > 0:
      damage = 2
      new_state["player_ammo"] -= 1
    
    if new_state["enemy_is_blocking"]:
      damage -= 1
      new_state["enemy_is_blocking"] = False
      
    new_state["enemy_life"] -= damage
  elif action == "block":
    new_state["player_is_blocking"] = True

  new_state["player"] = 1 if new_state["player"] == 2 else 2
  new_state["enemy"] = 2 if new_state["enemy"] == 1 else 1
  
  print("new_state", new_state)
  return new_state
  
def evaluate(state):
  pos_player, pos_enemy, pos_gun, pos_heart = get_board_positions(state["board"], state["player"], state["enemy"])
  print("evaluate", "state", state, "pos_player", pos_player, "pos_enemy", pos_enemy, "pos_gun", pos_gun, "pos_heart", pos_heart)
  score = 0
  
  player_gun_distance = 0
  enemy_gun_distance = 0
  player_heart_distance = 0
  enemy_heart_distance = 0
  if len(pos_gun) > 0:
    player_gun_distance = abs(pos_player[0] - pos_gun[0]) + abs(pos_player[1] - pos_gun[1])
    enemy_gun_distance = abs(pos_enemy[0] - pos_gun[0]) + abs(pos_enemy[1] - pos_gun[1])
  if len(pos_heart) > 0:
    player_heart_distance = abs(pos_player[0] - pos_heart[0]) + abs(pos_player[1] - pos_heart[1])
    enemy_heart_distance = abs(pos_enemy[0] - pos_heart[0]) + abs(pos_enemy[1] - pos_heart[1])
  
  if state["player_life"] < state["enemy_life"]:
    score -= 100
  elif state["player_life"] > state["enemy_life"]:
    score += 100
  elif state["player_life"] == state["enemy_life"]:
    score += 50
  elif state["enemy_life"] <= state["player_ammo"]:
    score += 200
  elif state["enemy_life"] * 2 <= state["player_ammo"]:
    score += 1000
  elif player_gun_distance > enemy_gun_distance:
    score -= 100
  elif state["player_life"] < state["enemy_life"] and player_heart_distance > enemy_heart_distance:
    score -= 200
  elif state["player_life"] < 9 and player_heart_distance < enemy_heart_distance:
    score += 200
  elif state["player_life"] == 9 and player_heart_distance < enemy_heart_distance:
    score -= 50
    
  score += (player_gun_distance + player_heart_distance) - (enemy_gun_distance * 2 + enemy_heart_distance * 2)
  return score

def endgame(state):
  if state["player_life"] <= 0 or state["enemy_life"] <= 0:
    return True
  return False

def minimax(state, depth, alpha, beta, maximizingPlayer):
  actions = all_possible_actions(state["board"], state["player"], state["enemy"])
  print("minimax_actions", actions, "depth", depth, "player", state["player"], "enemy", state["enemy"])
  
  if depth == 0 or endgame(state):
    return evaluate(state)
  
  if maximizingPlayer:
    maxEval = -INF
    for action in actions:
      new_state = mount_state(state, action, False)
      newEval = minimax(new_state, depth - 1, alpha, beta, False)
      maxEval = max(maxEval, newEval)
      alpha = max(alpha, newEval)
      if beta <= alpha:
        break
    return maxEval
  else:
    minEval = INF
    for action in actions:
      new_state = mount_state(state, action, False)
      newEval = minimax(new_state, depth - 1, alpha, beta, True)
      minEval = min(minEval, newEval)
      beta = min(beta, newEval)
      if beta <= alpha:
        break
    return minEval


initial_board = mount_board(board_arg)
initial_state = create_state_string(player, board_arg, life1, life2, bullet1, bullet2)
initial_depth = 3
best_action = None
best_score = -INF

for action in all_possible_actions(initial_board, player, enemy):
  new_state = mount_state(initial_state, action, True)
  score = minimax(new_state, initial_depth, -INF, INF, False)
  print("minimax_score", score, "action", action)
  if score > best_score:
    best_score = score
    best_action = action

print(best_action)