import math
import sys

GRID_SIZE = 5

class GameState:
  def __init__(self, player_turn, heart_pos, player1_pos, player2_pos, weapon_pos, player1_lives, player2_lives, player1_ammo, player2_ammo):
    self.player_turn = player_turn
    self.heart_pos = heart_pos
    self.player1_pos = player1_pos
    self.player2_pos = player2_pos
    self.weapon_pos = weapon_pos
    self.player1_lives = player1_lives
    self.player2_lives = player2_lives
    self.player1_ammo = player1_ammo
    self.player2_ammo = player2_ammo

  def get_possible_actions(self):
    actions = []
    player_pos = self.player1_pos if self.player_turn == 1 else self.player2_pos
    enemy_pos = self.player2_pos if self.player_turn == 1 else self.player1_pos

    def is_valid_command(command):
      player_xy = player_pos[:]
      enemy_xy = enemy_pos[:]

      if command == "up":
        if player_xy[1] == 0 or (player_xy[0] == enemy_xy[0] and player_xy[1] - 1 == enemy_xy[1]):
          return False
      elif command == "down":
        if player_xy[1] == GRID_SIZE - 1 or (player_xy[0] == enemy_xy[0] and player_xy[1] + 1 == enemy_xy[1]):
          return False
      elif command == "left":
        if player_xy[0] == 0 or (player_xy[0] - 1 == enemy_xy[0] and player_xy[1] == enemy_xy[1]):
          return False
      elif command == "right":
        if player_xy[0] == GRID_SIZE - 1 or (player_xy[0] + 1 == enemy_xy[0] and player_xy[1] == enemy_xy[1]):
          return False
      elif command == "attack":
        if abs(player_xy[0] - enemy_xy[0]) <= 1 and abs(player_xy[1] - enemy_xy[1]) <= 1:
          return True
        else:
          return False
      elif command == "block":
        return True
      else:
        return False

      return True

    # Check movement actions
    if is_valid_command("up"):
      actions.append("up")
    if is_valid_command("down"):
      actions.append("down")
    if is_valid_command("left"):
      actions.append("left")
    if is_valid_command("right"):
      actions.append("right")

    # Add block action
    if is_valid_command("block"):
      actions.append("block")

    # Add attack action if valid
    if is_valid_command("attack"):
      actions.append("attack")

    return actions

  def is_enemy_adjacent(self):
    player_pos = self.player1_pos if self.player_turn == 1 else self.player2_pos
    enemy_pos = self.player2_pos if self.player_turn == 1 else self.player1_pos
    return abs(player_pos[0] - enemy_pos[0]) + abs(player_pos[1] - enemy_pos[1]) == 1
  
  def apply_action(self, action):
      # Create a copy of the current state
      new_state = GameState(
        self.player_turn,
        self.heart_pos[:],
        self.player1_pos[:],
        self.player2_pos[:],
        self.weapon_pos[:],
        self.player1_lives,
        self.player2_lives,
        self.player1_ammo,
        self.player2_ammo
      )

      # Apply the action to the new state
      if action in ["up", "down", "left", "right"]:
        player_pos = new_state.player1_pos if new_state.player_turn == 1 else new_state.player2_pos
        if action == "up" and player_pos[1] > 0:
          player_pos[1] -= 1
        elif action == "down" and player_pos[1] < GRID_SIZE - 1:
          player_pos[1] += 1
        elif action == "left" and player_pos[0] > 0:
          player_pos[0] -= 1
        elif action == "right" and player_pos[0] < GRID_SIZE - 1:
          player_pos[0] += 1
      elif action == "attack" and new_state.is_enemy_adjacent():
        base_damage = 1
        if new_state.player_turn == 1:
          damage = base_damage + (1 if new_state.player1_ammo > 0 else 0) - (1 if new_state.player2_pos == "block" else 0)
          new_state.player2_lives -= damage
        else:
          damage = base_damage + (1 if new_state.player2_ammo > 0 else 0) - (1 if new_state.player1_pos == "block" else 0)
          new_state.player1_lives -= damage

      # Switch the turn to the other player
      new_state.player_turn = 2 if new_state.player_turn == 1 else 1

      return new_state

  def is_terminal(self):
    # Check if the game state is terminal
    return self.player1_lives == 0 or self.player2_lives == 0

  def evaluate(self):
    score = 0
    player_pos = self.player1_pos if self.player_turn == 1 else self.player2_pos
    enemy_pos = self.player2_pos if self.player_turn == 1 else self.player1_pos

    # Bonus for being closer to the weapon
    if self.weapon_pos:
        weapon_distance = abs(player_pos[0] - self.weapon_pos[0]) + abs(player_pos[1] - self.weapon_pos[1])
        score += (4 - weapon_distance) * 10  # The closer to the weapon, the higher the score

    # Bonus for attacking
    if self.is_enemy_adjacent():
      score += 50  # High bonus for being in a position to attack

    # Additional factors can be added here, such as health, ammo, etc.
    score += self.player1_lives * 20 if self.player_turn == 1 else self.player2_lives * 20
    score += self.player1_ammo * 5 if self.player_turn == 1 else self.player2_ammo * 5

    return score

def minimax(state, depth, alpha, beta, maximizing_player):
  if depth == 0 or state.is_terminal():
    return state.evaluate()

  if maximizing_player:
    max_eval = -math.inf
    for action in state.get_possible_actions():
      new_state = state.apply_action(action)
      eval = minimax(new_state, depth - 1, alpha, beta, False)
      max_eval = max(max_eval, eval)
      alpha = max(alpha, eval)
      if beta <= alpha:
        break
    return max_eval
  else:
    min_eval = math.inf
    for action in state.get_possible_actions():
      new_state = state.apply_action(action)
      eval = minimax(new_state, depth - 1, alpha, beta, True)
      min_eval = min(min_eval, eval)
      beta = min(beta, eval)
      if beta <= alpha:
        break
    return min_eval

def best_action(state):
  best_val = -math.inf
  best_move = None
  for action in state.get_possible_actions():
    new_state = state.apply_action(action)
    move_val = minimax(new_state, 5, -math.inf, math.inf, False)
    if move_val > best_val:
      best_val = move_val
      best_move = action
  return best_move

if __name__ == "__main__":
  # State from parameters
  player_turn = int(sys.argv[1]) 
  enemy = 1 if player_turn == 2 else 2 
  board = sys.argv[2]
  player1_lives = int(sys.argv[3])
  player2_lives = int(sys.argv[4])
  player1_ammo = int(sys.argv[5])
  player2_ammo = int(sys.argv[6])

  # Mounting matrix board
  board = list(board)
  res = []
  for idx in range(0, len(board) // GRID_SIZE):
    res.append(board[idx * GRID_SIZE : (idx + 1) * GRID_SIZE])
  board = [list(map(int, x)) for x in res]

  # Getting objects positions
  player1_pos = []
  player2_pos = []
  heart_pos = []
  weapon_pos = []
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if board[i][j] == player_turn:
            player1_pos = [j,i]
        elif board[i][j] == enemy:
            player2_pos = [j,i]
        elif board[i][j] == 3:
            weapon_pos = [j,i]
        elif board[i][j] == 4:
            heart_pos = [j,i]

  print('pos', player1_pos, player2_pos)

  state = GameState(player_turn, heart_pos, player1_pos, player2_pos, weapon_pos, player1_lives, player2_lives, player1_ammo, player2_ammo)
  print(best_action(state))