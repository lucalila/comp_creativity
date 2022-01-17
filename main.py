import pygame
import random
import sys
from pygame import QUIT

from classes import Player, Grid


# rules functions
def move(player, point):
    player.round += point
    if player.round >= 3:  # sum of grids
        player.round -= 3
        print_message('Over start, you have got 200$.', (35, 40))
        player.money += 200
    player.location = grids_pool[player.round].coor  # list of coordinates of grids


def print_message(text, position):
    text_surface = font.render(text, True, black)
    screen.blit(text_surface, position)


def pass_by(player, active_grid=None):
    for grid in grids_pool:
        if player.location == grid.coor:
            active_grid = grid

    if active_grid.chance:
        print_message(random.choice(action_texts), (35, 80))
        #  how to tell what actions take place? pay, gain...

    elif active_grid.owner:
        print_message('You should pay ' + active_grid.owner + ' ' + str(active_grid.rent) + ' Euro.', (35, 60))
        # changes from money of 2 players

    elif active_grid.stop:
        print_message('You should take a break.')
        player.pause = True

    elif active_grid.owner is None and active_grid.rent:
        active_grid.owner = player.name
        player.money -= active_grid.rent


# grids data
grids_dict = [((198, 200), False, False, None), ((340, 200), False, False, 200),
              ((482, 200), True, True, None)]  # list of tuple or dictionary
action_texts = ['Go forward', 'Go to jail']

# initialising
pygame.init()
clock = pygame.time.Clock()

size = (720, 405)
screen = pygame.display.set_mode(size)
map = pygame.image.load('./map/sample.bmp')  # filename of map needed, return map Surface
pygame.display.set_caption('Monopoly_Sample')
font = pygame.font.Font('/Library/Fonts/Arial Unicode.ttf', 20)
black = (0, 0, 0)
text_position = (34, 23)  # where should a text be printed

# initialize players and grids
player1 = pygame.image.load('./figure/player1.png')
player2 = pygame.image.load('./figure/player2.png')
player_pool = [Player('Player1', player1), Player('Player2', player2)]
grids_pool = [Grid(a, b, c, d) for a, b, c, d in grids_dict]

# surface reactions


# variables initializing
dice_point = 0
active_player = None

run = True

while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    #  how to start game?

    # a round start
    for active_player in player_pool:

        screen.blit(map, (0, 0))

        for player in player_pool:
            screen.blit(player.figure, player.location)

        dice_point = random.randint(1, 3)

        print_message('You have got a ' + str(dice_point), (35, 20))

        move(active_player, dice_point)
        # display update
        # screen.blit(active_player.figure, active_player.location)

        pass_by(active_player)

        # for player in player_pool:
        #     screen.blit(player.figure, player.location)

        # print(active_player.name)

        if active_player.money <= 0:
            print_message(active_player.name + 'lost.')
            run = False

    pygame.display.flip()
    clock.tick(1)
