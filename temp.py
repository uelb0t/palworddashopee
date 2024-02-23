tabuleiro = [[0, 0, 0, 0, 4], [0, 1, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 2, 0], [3, 0, 0, 0, 0]]
player = 2
enemy = 1 if player == 2 else 2

for linha in tabuleiro:
  for valor in linha:
    print(valor, end=" ")
  print()

def get_board_data(board, player, enemy):
  pos_player = []
  pos_enemy = []
  pos_weapon = []
  pos_heart = []
  for i in range(5):
    for j in range(5):
        if board[i][j] == player:
            pos_player = [j,i]
        elif board[i][j] == enemy:
            pos_enemy = [j,i]
        elif board[i][j] == 3:
            pos_weapon = [j,i]
        elif board[i][j] == 4:
            pos_heart = [j,i]

  return pos_player, pos_enemy, pos_weapon, pos_heart

print(get_board_data(tabuleiro, player, enemy))