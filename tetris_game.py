# =============================================================================#
# Name        : tetris_game.py                                                 #
# Description : Python version of the tetris game                              #
# Author      : Nguyen Vu Tuong Lam                                            #
# Date        : 08.11.2017                                                     #
# ---------------------------------------------------------------------------- #
# Updated     : 21.10.2019                                                     #
# Author      : Ronja Faltin, Johanna Granström, Emilie Ho                     #
# =============================================================================#

from random import randrange as rand

import pygame
import numpy as np

# The configuration
cell_size = 30
cell_size_inner = 25
cols = 6
rows = 12
max_fps = 60
font_size = 16
pygame.init()
pygame.mixer.init()

colors = [
    (0, 0, 0),
    (237, 80, 104),   # Pink
    (255, 176, 0),    # Orange
    (31, 163, 158),   # Blue-green
    (35, 51, 135),    # Blue
    (250, 128, 114),  # Salmon
    (230, 220, 210),  # Cream white
    (255, 119, 0),    # Yellow
    (20, 20, 20)      # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


# ================================================================================================#
#                                       Function Definitions                                     #
# ================================================================================================#


def rotate_clockwise(shape):
    return [[shape[y][x]
             for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    # Add score if a block is seated
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def create_board():
    board = [[0 for x in range(cols)]
             for y in range(rows)]
    board += [[1 for x in range(cols)]]
    return board


# ================================================================================================#
#                                       Main Game Part                                           #
# ================================================================================================#

class TetrisApp(object):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat()  # Delay in milliseconds (250, 25) -> No delay needed?
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.r_lim = cell_size * cols

        # Make the grid in the background, 8 and 3 is the color
        self.b_ground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

        #  Change the font in the game
        self.default_font = pygame.font.Font(
            pygame.font.get_default_font(), font_size)

        self.screen = pygame.display.set_mode((self.width, self.height))
        # We do not need mouse movement events, so we block them.
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.init_game()

        self.actions = {
            0: lambda: self.move(-1),  # Left
            1: lambda: self.move(+1),  # Right
            2: self.rotate_stone,      # Rotate
            3: self.instant_drop,      # Instant drop
            4: self.drop               # Doing nothing, only drops
        }

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = create_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        self.action_reward = 0
        self.stop_ai = False
        self.gameover = False

        # Init variables for the function bumpiness
        self.total_bumpiness = 0
        self.prev_col = float('NaN')  # Not to start outside of board
        self.col = 0
        self.bump_counter = 0

        # Init variables for the function aggregated height
        self.aggregated_height = 0
        self.height_prev_col = float('NaN')  # Not to start outside of board
        self.height_col = 0
        self.height_counter = 0

    def display_msg(self, msg, top_left):
        x, y = top_left
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(line, False, (255, 255, 255), (0, 0, 0)), (x, y))
            y += 30

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (0, 0, 255), (0, 0, 0))
            msg_im_center_x, msg_im_center_y = msg_image.get_size()
            msg_im_center_x //= 2
            msg_im_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msg_im_center_x,
                self.height // 2 - msg_im_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):

            for x, val in enumerate(row):

                if val:
                    pygame.draw.rect(self.screen, colors[val],
                                     pygame.Rect((off_x + x) * cell_size, (off_y + y) * cell_size, cell_size_inner,
                                                 cell_size_inner), 0)
                    pygame.draw.rect(self.screen, colors[val],
                                     pygame.Rect((off_x + x) * cell_size, (off_y + y) * cell_size, cell_size,
                                                 cell_size), 2)

    def add_cl_lines(self, n):
        self.lines += n
        # self.score += n*20 # -> Is now in get score instead

    def move(self, delta_x):
        if not self.gameover:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def get_state(self):
        return self.stone_x, self.stone_y

    def quit(self):
        self.center_msg("Exiting...")
        return self.stop_ai

    def drop(self):
        if not self.gameover:
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                self.new_stone()
                self.bumpiness()  # Calculate bumpiness when a stone is seated
                self.total_height()
                self.number_of_holes()
                # self.number_of_holes()  # Calculate number of holes when a stone is seated
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def instant_drop(self):
        if not self.gameover:
            while not self.drop():
                pass

    def rotate_stone(self):
        if not self.gameover:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    # Sum and maximum height of the board
    def total_height(self):
        self.aggregated_height = 0
        for c in zip(*self.board):

            for val in c:
                if val == 0:
                    self.height_counter += 1
                else:
                    break
            self.height_col = abs(self.height_counter - rows)
            if not np.isnan(self.height_prev_col):
                self.aggregated_height = self.aggregated_height + self.height_col

            self.height_prev_col = self.height_col
            self.height_col = 0
            self.height_counter = 0

        return self.aggregated_height

    # Calculate the bumpiness in the board
    def bumpiness(self):
        self.total_bumpiness = 0
        for c in zip(*self.board):

            for val in c:
                if val == 0:
                    self.bump_counter += 1
                else:
                    break
            self.col = abs(self.bump_counter - rows)
            if not np.isnan(self.prev_col):
                self.total_bumpiness = self.total_bumpiness + abs(self.prev_col - self.col)

            self.prev_col = self.col
            self.col = 0
            self.bump_counter = 0

        return self.total_bumpiness

    def number_of_holes(self):
        total_holes = 0
        holes_counter = 0
        prev_cell = float('NaN')

        for col in zip(*self.board):
            for val in col:
                if not np.isnan(prev_cell):  # If prev cell is not a number (For every new column)
                    if val == 0 and prev_cell != 0:
                        holes_counter += 1
                prev_cell = val

            # Do this for every column
            total_holes += holes_counter
            holes_counter = 0
            prev_cell = float('NaN')

        return total_holes

    def start_game(self, terminated):
        # print(terminated)
        self.gameover = terminated

        if not self.gameover:
            self.init_game()

    def get_reward(self):
        # Factors from 'Tetris AI – The (Near) Perfect Bot'
        a = -0.510066
        b = 0.760666
        c = -0.35663
        d = -0.184483

        self.action_reward = a * self.total_height() + b * self.lines + c * self.number_of_holes() + d * self.bumpiness()

        return self.action_reward

    def get_number_of_lines(self):
        return self.lines

    def reset_reward(self):
        self.score = 0
        self.action_reward = 0
        self.total_bumpiness = 0
        self.aggregated_height = 0

    def get_terminated(self):
        return self.gameover

    def play(self, action):
        self.action_from_agent = action
        for x in self.actions:
            if x == self.action_from_agent:
                self.actions[self.action_from_agent]()

        self.render_game()
        self.drop()

        # Declared new variables to make the return-line a reasonable length
        state = self.get_state()
        reward = self.get_reward()
        terminated = self.get_terminated()
        bumpiness = self.bumpiness()
        height = self.total_height()
        holes = self.number_of_holes()

        return state, reward, terminated, bumpiness, height, holes

    def render_game(self):
        dont_burn_my_cpu = pygame.time.Clock()

        # Fills the screen background with black (RGB)
        self.screen.fill((0, 0, 0))

        pygame.draw.line(self.screen,
                         (255, 255, 255),
                         (self.r_lim + 1, 0),
                         (self.r_lim + 1, self.height - 1))
        self.display_msg("Next:", (
            self.r_lim + cell_size,
            2))
        self.display_msg("Score: %d\nLines: %d\nAction reward: %d\nAction: %d\nBumpiness: %d\nTotal height: "
                         "%d\nHoles: %d" % (self.score, self.lines, self.get_reward(), self.action_from_agent,
                                            self.bumpiness(), self.total_height(), self.number_of_holes()),
                         (self.r_lim + cell_size, cell_size * 5))

        self.draw_matrix(self.b_ground_grid, (0, 0))
        self.draw_matrix(self.board, (0, 0))
        self.draw_matrix(self.stone,
                         (self.stone_x, self.stone_y))
        self.draw_matrix(self.next_stone,
                         (cols + 1, 2))

        # Need to just handle event in pygame to be able to move window
        for event in pygame.event.get():
            # If you cross down the window and exiting
            if event.type == pygame.QUIT:
                self.stop_ai = True
                self.quit()

        pygame.display.update()
        dont_burn_my_cpu.tick(max_fps)
