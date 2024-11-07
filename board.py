from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import os
import random
import time
import subprocess

pygame.init()

# Configuration
PROGRAM_1 = ['python3', 'ia_normal.py']
WIDTH, HEIGHT = 500, 500
GRID_SIZE = 5
def is_valid_position(pos, positions, min_distance=2):
    for p in positions:
        if abs(pos % GRID_SIZE - p % GRID_SIZE) < min_distance and abs(pos // GRID_SIZE - p // GRID_SIZE) < min_distance:
            return False
    return True

POS_PLAYER_1 = random.randint(0, GRID_SIZE*GRID_SIZE - 1)
POS_PLAYER_2 = random.randint(0, GRID_SIZE*GRID_SIZE - 1)
while not is_valid_position(POS_PLAYER_2, [POS_PLAYER_1]):
    POS_PLAYER_2 = random.randint(0, GRID_SIZE*GRID_SIZE - 1)

POS_GUN = random.randint(0, GRID_SIZE*GRID_SIZE - 1)
while not is_valid_position(POS_GUN, [POS_PLAYER_1, POS_PLAYER_2]):
    POS_GUN = random.randint(0, GRID_SIZE*GRID_SIZE - 1)

POS_HEART = random.randint(0, GRID_SIZE*GRID_SIZE - 1)
while not is_valid_position(POS_HEART, [POS_PLAYER_1, POS_PLAYER_2, POS_GUN]):
    POS_HEART = random.randint(0, GRID_SIZE*GRID_SIZE - 1)

AMMO = 5

# State
# 0 empty
# 1 player 1
# 2 player 2
# 3 gun
# 4 heart
# life 1, life 2, gun 1, gun 2
board = [0 for _ in range(GRID_SIZE*GRID_SIZE)]
pos_player1 = POS_PLAYER_1
pos_player2 = POS_PLAYER_2
pos_gun = POS_GUN
pos_heart = POS_HEART
board[pos_player1] = 1
board[pos_player2] = 2
board[pos_gun] = 3
board[pos_heart] = 4
lifes = [9, 9]
bullets = [0, 0]
block = [0, 0]

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT+50))
pygame.display.set_caption("Palword da Shopee")
background = pygame.image.load(os.path.join("images", "background.png")).convert()
player1 = pygame.image.load(os.path.join("images", "palA100.png")).convert_alpha()
player2 = pygame.image.load(os.path.join("images", "palB100.png")).convert_alpha()
gun = pygame.image.load(os.path.join("images", "gun.png")).convert_alpha()
heart = pygame.image.load(os.path.join("images", "heart.png")).convert_alpha()
attack = pygame.image.load(os.path.join("images", "attack.png")).convert_alpha()
defense = pygame.image.load(os.path.join("images", "block.png")).convert_alpha()
player1_turn = random.randint(0, 1)

# Music 
background_music = pygame.mixer.music.load(os.path.join("sounds", "calor_blanco.mp3"))
pygame.mixer.music.set_volume(0.1)
# Sounds
default_attack_sound = pygame.mixer.Sound(os.path.join("sounds", "default_attack.mp3"))
gunfire_sound = pygame.mixer.Sound(os.path.join("sounds", "gunfire.mp3"))
block_sound = pygame.mixer.Sound(os.path.join("sounds", "shield_block.mp3"))
heal_sound = pygame.mixer.Sound(os.path.join("sounds", "heal.mp3"))
walking_sound = pygame.mixer.Sound(os.path.join("sounds", "walking.mp3"))

font = pygame.font.SysFont("comicsans", 20, True)


def play_sound(sound):
    pygame.mixer.Sound.play(sound, maxtime=500, fade_ms=100)

# Difficulty selector
difficulty_selected = False
difficulty = "normal"

def draw_difficulty_selector():
    screen.fill((0, 0, 0))
    normal_text = font.render("Aperte N para jogar no modo Normal", True, (255, 255, 255))
    hard_text = font.render("Aperte D para jogar no modo Difícil", True, (255, 255, 255))
    screen.blit(normal_text, (WIDTH // 2 - normal_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

while not difficulty_selected:
    draw_difficulty_selector()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                difficulty = "normal"
                difficulty_selected = True
            elif event.key == pygame.K_d:
                difficulty = "hard"
                difficulty_selected = True

# Adjust game parameters based on difficulty
if difficulty == "hard":
    AMMO = 3
    PROGRAM_1 = ['python3', 'ia_hard.py']

def is_valid_command(command):
    player_xy = [pos_player1 % GRID_SIZE, pos_player1 // GRID_SIZE]
    enemy_xy = [pos_player2 % GRID_SIZE, pos_player2 // GRID_SIZE]
    print(player_xy, enemy_xy)

    if not player1_turn:
        player_xy = enemy_xy
        enemy_xy = [pos_player1 % GRID_SIZE, pos_player1 // GRID_SIZE]

    if command == "up":
        if player_xy[1] == 0 or (player_xy[0] == enemy_xy[0] and player_xy[1]-1 == enemy_xy[1]):
            return False
    elif command == "down":
        if player_xy[1] == GRID_SIZE-1 or (player_xy[0] == enemy_xy[0] and player_xy[1]+1 == enemy_xy[1]):
            return False
    elif command == "left":
        if player_xy[0] == 0 or (player_xy[0]-1 == enemy_xy[0] and player_xy[1] == enemy_xy[1]):
            return False
    elif command == "right":
        if player_xy[0] == GRID_SIZE-1 or (player_xy[0]+1 == enemy_xy[0] and player_xy[1] == enemy_xy[1]):
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

# Update screen
def updateScreen(status, player1_attack, player2_attack):
    # x,y positions
    player1_xy = [(pos_player1 % GRID_SIZE) * (WIDTH//(GRID_SIZE)), (pos_player1 // GRID_SIZE) * (HEIGHT//(GRID_SIZE))]
    player2_xy = [(pos_player2 % GRID_SIZE) * (WIDTH//(GRID_SIZE)), (pos_player2 // GRID_SIZE) * (HEIGHT//(GRID_SIZE))]
    
    screen.blit(background, (0, 0))
    screen.blit(player1, player1_xy)
    screen.blit(player2, player2_xy)

    # drawing gun if available
    if pos_gun >= 0:
        gun_xy = [(pos_gun % GRID_SIZE) * (WIDTH//(GRID_SIZE)) + 10, (pos_gun // GRID_SIZE) * (HEIGHT//(GRID_SIZE)) + 10]
        screen.blit(gun, gun_xy)

    # drawing heart if available
    if pos_heart >= 0:
        heart_xy = [(pos_heart % GRID_SIZE) * (WIDTH//(GRID_SIZE)) + 15, (pos_heart // GRID_SIZE) * (HEIGHT//(GRID_SIZE)) + 15]
        screen.blit(heart, heart_xy)

    # Health Bar
    healthBarOffset1 = 0
    healthBarOffset2 = 0
    if pos_player1 < GRID_SIZE:
        healthBarOffset1 = 80
    if pos_player2 < GRID_SIZE:
        healthBarOffset2 = 80
    pygame.draw.rect(screen, (255,0,0), (player1_xy[0] + 20, player1_xy[1] - 15 + healthBarOffset1, 45, 10))
    pygame.draw.rect(screen, (0,128,0), (player1_xy[0] + 20, player1_xy[1] - 15 + healthBarOffset1, 45 - (5 * (9 - lifes[0])), 10))
    pygame.draw.rect(screen, (255,0,0), (player2_xy[0] + 20, player2_xy[1] - 15 + healthBarOffset2, 45, 10))
    pygame.draw.rect(screen, (0,128,0), (player2_xy[0] + 20, player2_xy[1] - 15 + healthBarOffset2, 45 - (5 * (9 - lifes[1])), 10))

    # Bullets
    for i in range(bullets[0]):
        pygame.draw.circle(screen, (50,50,50), [player1_xy[0] + 25+i*8, player1_xy[1] - 10], 3, 0)
    for i in range(bullets[1]):
        pygame.draw.circle(screen, (50,50,50), [player2_xy[0] + 25+i*8, player2_xy[1] - 10], 3, 0)

    # Attack
    if player1_attack:
        screen.blit(attack, (player1_xy[0]-100,player1_xy[1]-100))
    elif player2_attack:
        screen.blit(attack, (player2_xy[0]-100,player2_xy[1]-100))

    # Block
    if block[0]:
        screen.blit(defense, (player1_xy[0]-100,player1_xy[1]-100))
    elif block[1]:
        screen.blit(defense, (player2_xy[0]-100,player2_xy[1]-100))

    # set status: text, anti-aliasing, color
    pygame.draw.rect(screen, (0,128,0), (0, 500, WIDTH, 50))
    status = font.render(status, 1, (255,255,255)) 
    screen.blit(status, (20, 500))
    
    pygame.display.flip()

# Update state after a command from a player
# Commands: up, down, left, right, attack, block
def updateState(command):

    global pos_player1, pos_player2, pos_gun, pos_heart, bullets, lifes

    player_index = 0 
    player_xy = [pos_player1 % GRID_SIZE, pos_player1 // GRID_SIZE]
    enemy_xy = [pos_player2 % GRID_SIZE, pos_player2 // GRID_SIZE]
    gun_xy = [pos_gun % GRID_SIZE, pos_gun // GRID_SIZE]
    heart_xy = [pos_heart % GRID_SIZE, pos_heart // GRID_SIZE]

    status = "Jogador 1"
    player1_attack = False
    player2_attack = False

    if not player1_turn:
        player_index = 1
        player_xy = enemy_xy
        enemy_xy = [pos_player1 % GRID_SIZE, pos_player1 // GRID_SIZE]
        status = "Jogador 2"

    block[player_index] = 0

    if command == "up":
        if player_xy[1] == 0 or (player_xy[0] == enemy_xy[0] and player_xy[1]-1 == enemy_xy[1]):
            status += " - Impossível mover"
        else:
            status += " - Moveu para cima"
            play_sound(walking_sound)
            # Got a gun?
            if player_xy[0] == gun_xy[0] and player_xy[1]-1 == gun_xy[1]:
                bullets[player_index] += AMMO
                pos_gun = -1
                status += " - Pegou arma"
            # Got a heart?
            if player_xy[0] == heart_xy[0] and player_xy[1]-1 == heart_xy[1]:
                lifes[player_index] = 9
                pos_heart = -1
                status += " - Pegou vida"
                play_sound(heal_sound)
            if player1_turn:
                board[pos_player1] = 0
                pos_player1 = pos_player1 - GRID_SIZE
                board[pos_player1] = 1
            else:
                board[pos_player2] = 0
                pos_player2 = pos_player2 - GRID_SIZE
                board[pos_player2] = 2

    if command == "down":
        if player_xy[1] == GRID_SIZE-1 or (player_xy[0] == enemy_xy[0] and player_xy[1]+1 == enemy_xy[1]):
            status += " - Impossível mover"
        else:
            status += " - Moveu para baixo"
            play_sound(walking_sound)
            # Got a gun?
            if player_xy[0] == gun_xy[0] and player_xy[1]+1 == gun_xy[1]:
                bullets[player_index] += AMMO
                pos_gun = -1
                status += " - Pegou arma"
            # Got a heart?
            if player_xy[0] == heart_xy[0] and player_xy[1]+1 == heart_xy[1]:
                lifes[player_index] = 9
                pos_heart = -1
                status += " - Pegou vida"
                play_sound(heal_sound)
            if player1_turn:
                board[pos_player1] = 0
                pos_player1 = pos_player1 + GRID_SIZE
                board[pos_player1] = 1
            else:
                board[pos_player2] = 0
                pos_player2 = pos_player2 + GRID_SIZE
                board[pos_player2] = 2

    if command == "left":
        if player_xy[0] == 0 or (player_xy[0]-1 == enemy_xy[0] and player_xy[1] == enemy_xy[1]):
            status += " - Impossível mover"
        else:
            status += " - Moveu para esquerda"
            play_sound(walking_sound)
            # Got a gun?
            if player_xy[0]-1 == gun_xy[0] and player_xy[1] == gun_xy[1]:
                bullets[player_index] += AMMO
                pos_gun = -1
                status += " - Pegou arma"
            # Got a heart?
            if player_xy[0]-1 == heart_xy[0] and player_xy[1] == heart_xy[1]:
                lifes[player_index] = 9
                pos_heart = -1
                status += " - Pegou vida"
                play_sound(heal_sound)
            if player1_turn:
                board[pos_player1] = 0
                pos_player1 = pos_player1 - 1
                board[pos_player1] = 1
            else:
                board[pos_player2] = 0
                pos_player2 = pos_player2 - 1
                board[pos_player2] = 2

    if command == "right":
        if player_xy[0] == GRID_SIZE-1 or (player_xy[0]+1 == enemy_xy[0] and player_xy[1] == enemy_xy[1]):
            status += " - Impossível mover"
        else:
            status += " - Moveu para direita"
            play_sound(walking_sound)
            # Got a gun?
            if player_xy[0]+1 == gun_xy[0] and player_xy[1] == gun_xy[1]:
                bullets[player_index] += AMMO
                pos_gun = -1
                status += " - Pegou arma"
            # Got a heart?
            if player_xy[0]+1 == heart_xy[0] and player_xy[1] == heart_xy[1]:
                lifes[player_index] = 9
                pos_heart = -1
                status += " - Pegou vida"
                play_sound(heal_sound)
            if player1_turn:
                board[pos_player1] = 0
                pos_player1 = pos_player1 + 1
                board[pos_player1] = 1
            else:
                board[pos_player2] = 0
                pos_player2 = pos_player2 + 1
                board[pos_player2] = 2
    
    elif command == "attack":
        sound = default_attack_sound
        damage = 1

        if player1_turn:
            player1_attack = True
        else:
            player2_attack = True

        # If the player has bullets
        if bullets[player_index] > 0:
            damage = 2
            bullets[player_index] = bullets[player_index] - 1
            sound = gunfire_sound
        
        # Enemy is blocking?
        if block[not player_index]:
            damage = damage - 1
            play_sound(block_sound)

        # Enemy is close?
        if abs(player_xy[0] - enemy_xy[0]) <= 1 and abs(player_xy[1] - enemy_xy[1]) <= 1:
            lifes[not player_index] -= damage
            status += " - Atacou e tirou " + str(damage) + " de vida"
            play_sound(sound)
        else:
            status += " - Atacou e errou"
            
    elif command == "block":
        block[player_index] = 1
        status += " - Defendeu"
        play_sound(block_sound)

    return status, player1_attack, player2_attack

updateScreen("Jogo iniciado", False, False)

# Game loop
running = True
pygame.mixer.music.play(-1)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if player1_turn:
        keys = pygame.key.get_pressed()
        command = None
        if keys[pygame.K_UP]:
            command = "up"
        elif keys[pygame.K_DOWN]:
            command = "down"
        elif keys[pygame.K_LEFT]:
            command = "left"
        elif keys[pygame.K_RIGHT]:
            command = "right"
        elif keys[pygame.K_a]:
            command = "attack"
        elif keys[pygame.K_b]:
            command = "block"

        if command:
            if is_valid_command(command):
                status, player1_attack, player2_attack = updateState(command)
                updateScreen(status, player1_attack, player2_attack)
                player1_turn = not player1_turn
            else:
                updateScreen("Comando inválido. Tente novamente.", False, False)
            time.sleep(0.3)
    else:
        parameter = PROGRAM_1 + ['2'] + [''.join(str(item) for item in board)] + [str(lifes[0]), str(lifes[1])] + [str(bullets[0]), str(bullets[1])]
        print(' '.join(parameter))
        command = subprocess.check_output(' '.join(parameter), shell=True).decode('utf-8').strip()
        print('ia_command', command)
        time.sleep(0.5)

        if is_valid_command(command):
            status, player1_attack, player2_attack = updateState(command)
            updateScreen(status, player1_attack, player2_attack)
            player1_turn = not player1_turn
        else:
            updateScreen("Comando inválido. Tente novamente.", False, False)

    # Game Over!
    if lifes[0] <= 0 or lifes[1] <= 0:
        running = False
        if lifes[0] <= 0:
            updateScreen("Jogador 2 venceu!", False, False)
        else:
            updateScreen("Jogador 1 venceu!", False, False)
        pygame.mixer.music.fadeout(4900)
        time.sleep(5)
        
pygame.quit()