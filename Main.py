import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Load sounds
Xmove_sound = pygame.mixer.Sound(r"C:\Users\david\OneDrive\Desktop\David\Programming\Tictactoetwist\Sound\Xmove.mp3")
Omove_sound = pygame.mixer.Sound(r"C:\Users\david\OneDrive\Desktop\David\Programming\Tictactoetwist\Sound\Omove.mp3")
winner_sound = pygame.mixer.Sound(r"C:\Users\david\OneDrive\Desktop\David\Programming\Tictactoetwist\Sound\Winner.mp3")

# Screen settings
WIDTH, HEIGHT = 700, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe-Twist")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 200, 0)

# Fonts
TITLE_FONT = pygame.font.SysFont('Arial', 60)
INSTRUCTION_FONT = pygame.font.SysFont('Arial', 24)
BUTTON_FONT = pygame.font.SysFont('Arial', 32)
MOVE_FONT = pygame.font.SysFont('Arial', 80)

# Board settings
CELL_SIZE = 200
GRID_ORIGIN_X = (WIDTH - 3 * CELL_SIZE) // 2  # Center the grid horizontally
GRID_ORIGIN_Y = 100

# Game states
TITLE, INSTRUCTIONS, SELECT_MODE, SELECT_DIFFICULTY, PLAYING, GAME_OVER, SHOW_WINNER = range(7)
state = TITLE

# Game variables
board = [['' for _ in range(3)] for _ in range(3)]
player_turn = 'X'
move_history = {'X': [], 'O': []}
winner = None
winning_line = None
vs_cpu = False
cpu_difficulty = 'Easy'
scores = {'X': 0, 'O': 0}
show_winner_time = 0
cpu_move_timer = None

# Button class
class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback

    def draw(self, active=False):
        color = GREEN if active else RED
        pygame.draw.rect(SCREEN, color, self.rect)
        text_surf = BUTTON_FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        SCREEN.blit(text_surf, text_rect)

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

# Functions
def start_instructions():
    global state
    state = INSTRUCTIONS

def start_select_mode():
    global state
    state = SELECT_MODE

def start_select_difficulty():
    global state
    state = SELECT_DIFFICULTY

def start_playing():
    global state
    state = PLAYING

def play_vs_player():
    global vs_cpu
    vs_cpu = False
    start_playing()

def play_vs_cpu():
    global vs_cpu
    vs_cpu = True
    start_select_difficulty()

def set_difficulty(level):
    global cpu_difficulty, state
    cpu_difficulty = level
    if state == SELECT_DIFFICULTY:
        state = PLAYING

def reset_game():
    global board, move_history, player_turn, winner, winning_line, state
    board = [['' for _ in range(3)] for _ in range(3)]
    move_history = {'X': [], 'O': []}
    player_turn = 'X'
    winner = None
    winning_line = None
    state = PLAYING

# Create buttons
# Total width of all buttons + spaces between them
button_width = 150
button_height = 40
button_spacing = 20

total_width = button_width * 3 + button_spacing * 2
start_x = (WIDTH - total_width) // 2  # Center starting point

cpu_button = Button("Vs. CPU", (WIDTH - button_width) // 2, 300, button_width, button_height, play_vs_cpu)
player_button = Button("Vs. Player", (WIDTH - button_width) // 2, 400, button_width, button_height, play_vs_player)
easy_button = Button("Easy", start_x, 750, button_width, button_height, lambda: set_difficulty('Easy'))
medium_button = Button("Medium", start_x + button_width + button_spacing, 750, button_width, button_height, lambda: set_difficulty('Medium'))
hard_button = Button("Hard", start_x + (button_width + button_spacing) * 2, 750, button_width, button_height, lambda: set_difficulty('Hard'))
play_again_button = Button("Play Again", 200, 700, 200, 50, reset_game)

# Draw functions
def draw_grid():
    for x in range(1, 3):
        # Horizontal lines
        pygame.draw.line(SCREEN, GREEN, 
                         (GRID_ORIGIN_X, GRID_ORIGIN_Y + x * CELL_SIZE), 
                         (GRID_ORIGIN_X + 3 * CELL_SIZE, GRID_ORIGIN_Y + x * CELL_SIZE), 5)
        # Vertical lines
        pygame.draw.line(SCREEN, GREEN, 
                         (GRID_ORIGIN_X + x * CELL_SIZE, GRID_ORIGIN_Y), 
                         (GRID_ORIGIN_X + x * CELL_SIZE, GRID_ORIGIN_Y + 3 * CELL_SIZE), 5)

def draw_moves():
    for r in range(3):
        for c in range(3):
            move = board[r][c]
            if move:
                color = RED if move == 'X' else BLUE
                text = MOVE_FONT.render(move, True, color)
                SCREEN.blit(text, 
                            (GRID_ORIGIN_X + c * CELL_SIZE + CELL_SIZE // 2 - text.get_width() // 2, 
                             GRID_ORIGIN_Y + r * CELL_SIZE + CELL_SIZE // 2 - text.get_height() // 2))

def highlight_winner():
    if winning_line:
        start_pos = (GRID_ORIGIN_X + winning_line[0][0] * CELL_SIZE + CELL_SIZE // 2, 
                     GRID_ORIGIN_Y + winning_line[0][1] * CELL_SIZE + CELL_SIZE // 2)
        end_pos = (GRID_ORIGIN_X + winning_line[1][0] * CELL_SIZE + CELL_SIZE // 2, 
                   GRID_ORIGIN_Y + winning_line[1][1] * CELL_SIZE + CELL_SIZE // 2)
        pygame.draw.line(SCREEN, YELLOW, start_pos, end_pos, 10)

def check_win():
    global winner, winning_line
    for p in ['X', 'O']:
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] == p:
                winner = p
                winning_line = [(0, i), (2, i)]
                return
            if board[0][i] == board[1][i] == board[2][i] == p:
                winner = p
                winning_line = [(i, 0), (i, 2)]
                return
        if board[0][0] == board[1][1] == board[2][2] == p:
            winner = p
            winning_line = [(0, 0), (2, 2)]
            return
        if board[0][2] == board[1][1] == board[2][0] == p:
            winner = p
            winning_line = [(2, 0), (0, 2)]
            return

def make_move(row, col):
    global player_turn, show_winner_time, state, winner
    if board[row][col] == '' and winner is None:
        board[row][col] = player_turn
        move_history[player_turn].append((row, col))
        if len(move_history[player_turn]) > 3:
            old_row, old_col = move_history[player_turn].pop(0)
            board[old_row][old_col] = ''
        if player_turn == 'X':
            Xmove_sound.play()
        else:
            Omove_sound.play()
        animate_move(row, col, player_turn)
        check_win()
        if winner:
            if winner != 'Draw':
                scores[winner] += 1
                winner_sound.play()
                pygame.time.set_timer(pygame.USEREVENT, 2000)  # Set a timer to fade out after 2 seconds
            state = SHOW_WINNER
            show_winner_time = time.time()
        elif all(board[r][c] != '' for r in range(3) for c in range(3)):
            winner = 'Draw'
            state = SHOW_WINNER
            show_winner_time = time.time()
        else:
            player_turn = 'O' if player_turn == 'X' else 'X'

def animate_move(row, col, player):
    for size in range(0, 100, 10):  # Grow animation
        SCREEN.fill(BLACK)
        draw_grid()
        draw_moves()
        highlight_winner()
        color = RED if player == 'X' else BLUE
        font = pygame.font.SysFont('Arial', size)
        text = font.render(player, True, color)
        x = GRID_ORIGIN_X + col * CELL_SIZE + CELL_SIZE // 2 - text.get_width() // 2
        y = GRID_ORIGIN_Y + row * CELL_SIZE + CELL_SIZE // 2 - text.get_height() // 2
        SCREEN.blit(text, (x, y))
        pygame.display.update()
        pygame.time.delay(20)
    for size in range(100, 80, -5):  # Shrink animation
        SCREEN.fill(BLACK)
        draw_grid()
        draw_moves()
        highlight_winner()
        color = RED if player == 'X' else BLUE
        font = pygame.font.SysFont('Arial', size)
        text = font.render(player, True, color)
        x = GRID_ORIGIN_X + col * CELL_SIZE + CELL_SIZE // 2 - text.get_width() // 2
        y = GRID_ORIGIN_Y + row * CELL_SIZE + CELL_SIZE // 2 - text.get_height() // 2
        SCREEN.blit(text, (x, y))
        pygame.display.update()
        pygame.time.delay(20)

def cpu_move():
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == '']
    if not empty:
        return
    if cpu_difficulty == 'Easy':
        make_move(*random.choice(empty))
    elif cpu_difficulty == 'Medium':
        for r, c in empty:
            board[r][c] = 'O'
            if winner_check_temp('O'):
                board[r][c] = ''
                make_move(r, c)
                return
            board[r][c] = ''
        make_move(*random.choice(empty))
    elif cpu_difficulty == 'Hard':
        for r, c in empty:
            board[r][c] = 'O'
            if winner_check_temp('O'):
                board[r][c] = ''
                make_move(r, c)
                return
            board[r][c] = ''
        for r, c in empty:
            board[r][c] = 'X'
            if winner_check_temp('X'):
                board[r][c] = ''
                make_move(r, c)
                return
            board[r][c] = ''
        make_move(*random.choice(empty))

def winner_check_temp(p):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] == p:
            return True
        if board[0][i] == board[1][i] == board[2][i] == p:
            return True
    if board[0][0] == board[1][1] == board[2][2] == p:
        return True
    if board[0][2] == board[1][1] == board[2][0] == p:
        return True
    return False

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    SCREEN.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT:
            winner_sound.fadeout(1000)  # Fade out smoothly over 1 second
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if state == TITLE:
                start_instructions()
            elif state == INSTRUCTIONS:
                start_select_mode()
            elif state == SELECT_MODE:
                cpu_button.click(pos)
                player_button.click(pos)
            elif state == SELECT_DIFFICULTY:
                easy_button.click(pos)
                medium_button.click(pos)
                hard_button.click(pos)
            elif state == PLAYING:
                if player_turn == 'X' or not vs_cpu:
                    if pos[1] > GRID_ORIGIN_Y and pos[1] < HEIGHT - 100:
                        row = (pos[1] - GRID_ORIGIN_Y) // CELL_SIZE
                        col = pos[0] // CELL_SIZE
                        make_move(row, col)
                if pos[1] >= 750:
                    if pos[0] < 200:
                        set_difficulty('Easy')
                    elif pos[0] < 400:
                        set_difficulty('Medium')
                    else:
                        set_difficulty('Hard')
            elif state == SHOW_WINNER:
                play_again_button.click(pos)

    if state == TITLE:
        title = TITLE_FONT.render("Tic-Tac-Toe-Twist", True, WHITE)
        SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 50))
    elif state == INSTRUCTIONS:
        instr1 = INSTRUCTION_FONT.render("A twist on classic Tic-Tac-Toe!", True, WHITE)
        instr2 = INSTRUCTION_FONT.render("On your 4th move and beyond, your oldest move vanishes!", True, WHITE)
        SCREEN.blit(instr1, (WIDTH//2 - instr1.get_width()//2, HEIGHT//2 - 20))
        SCREEN.blit(instr2, (WIDTH//2 - instr2.get_width()//2, HEIGHT//2 + 20))
    elif state == SELECT_MODE:
        cpu_button.draw()
        player_button.draw()
    elif state == SELECT_DIFFICULTY:
        easy_button.draw(active=(cpu_difficulty == 'Easy'))
        medium_button.draw(active=(cpu_difficulty == 'Medium'))
        hard_button.draw(active=(cpu_difficulty == 'Hard'))
    elif state == PLAYING:
        draw_grid()
        draw_moves()
        highlight_winner()
        score = INSTRUCTION_FONT.render(f"X: {scores['X']}  O: {scores['O']}", True, WHITE)
        SCREEN.blit(score, (10, 10))
        easy_button.draw(active=(cpu_difficulty == 'Easy'))
        medium_button.draw(active=(cpu_difficulty == 'Medium'))
        hard_button.draw(active=(cpu_difficulty == 'Hard'))
    elif state == SHOW_WINNER:
        draw_grid()
        draw_moves()
        highlight_winner()
        if winner == 'Draw':
            win_text = TITLE_FONT.render("It's a Draw!", True, WHITE)
        else:
            win_text = TITLE_FONT.render(f"{'Player 1' if winner == 'X' else 'Player 2'} Wins!", True, WHITE)
        SCREEN.blit(win_text, (WIDTH//2 - win_text.get_width()//2, 20))
        play_again_button.draw()

    pygame.display.update()

    if vs_cpu and player_turn == 'O' and state == PLAYING:
        if cpu_move_timer is None:
            cpu_move_timer = time.time()
        elif time.time() - cpu_move_timer >= 1:
            cpu_move()
            cpu_move_timer = None
    else:
        cpu_move_timer = None

    clock.tick(60)

pygame.quit()
sys.exit()