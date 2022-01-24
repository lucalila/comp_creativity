import pygame
import random
import sys
from pygame import QUIT
from dimension import Dimension
from classes import Player, Grid
from create_map import create_a_map


locations = list()
action_cards = list()
map_path = None
topic = None
map = None


def change_dimension():
    global locations
    global action_cards
    global map_path
    global map
    global topic
    dimension = Dimension()
    dimension.change_topic()
    dimension.generate_locations()
    dimension.generate_action_cards()
    locations = dimension.locations
    action_cards = dimension.action_cards
    topic = dimension.topic
    map_path = create_a_map(locations, topic)
    map = pygame.image.load(map_path).convert_alpha()
    # print(dimension.new_field)
    # change Grids name
    grids_to_be_changed = [6, 8, 9, 11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29, 31, 32, 34, 37, 39, 1, 3, 12, 28, 5, 15, 25, 35, 30, 20]
    for i in range(0, 30):
        grids_pool[grids_to_be_changed[i]].name = locations[i + 1]


def print_money():
    player1_money = f'{Player1.name}: {Player1.money}'
    player2_money = f'{Player2.name}: {Player2.money}'
    print_message(player1_money, (850, 250))
    print_message(player2_money, (850, 280))


def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)


def take_a_action(player, action_tuple):
    if action_tuple[2]:
        for grid in grids_pool:
            if action_tuple[2] == grid.name:
                target_grid = grid
                player.location = target_grid.coor
                player.round_count = grids_pool.index(target_grid)
    elif action_tuple[1] == 'positive':
        player.money += int(action_tuple[3])
    elif action_tuple[1] == 'negative':
        player.money += int(action_tuple[3])


def lose(player):
    if player.money <= 0:
        print_message(f'{player.name} does not have money any more! ')
        for p in player_pool:
            if player != p:
                print_message(f'{p.name} has won!')
                # sys.exit()


# rules functions
def move(player, point):
    player.round_count += point
    if player.round_count >= 39:  # sum of grids
        player.round_count -= 39
        change_dimension()
        print_message('Dimension has now changed to ' + topic + ' !')
        print_message('Over start, you have got 200$.')
        player.money += 200
    player.location = grids_pool[player.round_count].coor  # list of coordinates of grids


def print_message(text, position=None):
    if position:
        text_surface = font.render(text, True, black)
        screen.blit(text_surface, position)
    else:
        global text_position
        text_surface = font.render(text, True, black)
        screen.blit(text_surface, message_coors[text_position])
        text_position += 1
        if text_position > 4:
            text_position -= 5


def pass_by(player, active_grid=None):

    for grid in grids_pool:
        if player.location == grid.coor:
            active_grid = grid
    print_message(f'{player.name} is now at {active_grid.name}!')

    if active_grid.chance:
        chance = random.choice(action_cards)
        print_message(chance[0])
        take_a_action(player, chance)

    elif active_grid.tax:
        print_message(f'{player.name} should pay {active_grid.tax} for {active_grid.name}.')
        player.money -= active_grid.tax

    elif active_grid.owner:
        print_message(f'{player.name} should pay ' + active_grid.owner + ' ' + str(active_grid.rent) + ' Euro.')
        player.money -= active_grid.rent
        for p in player_pool:
            if player != p:
                p.money += active_grid.rent

    elif active_grid.stop:
        print_message(f'{player.name} should take a break.')
        player.pause = True
        if active_grid.coor == (1074, 15):
            player.round = 10
            player.location = (30, 1100)

    elif active_grid.owner is None and active_grid.rent:
        print_message(f'The {active_grid.name} now belongs to {player.name}!')
        active_grid.owner = player.name
        player.money -= active_grid.rent


if __name__ == '__main__':
    # grids data
    grids_tuples = [((1100, 1100), False, None, False, None), ((968, 1096), False, None, False, 60),
                    ((870, 1096), True, None, False, None), ((772, 1096), False, None, False, 60),
                    ((670, 1096), False, 200, False, None), ((572, 1050), False, None, False, 200), \
                    ((474, 1096), False, None, False, 100), ((376, 1096), True, None, False, None),
                    ((278, 1096), False, None, False, 100), ((180, 1096), False, None, False, 120), \
                    ((30, 1100), False, None, False, None), ((35, 964), False, None, False, 140),
                    ((70, 866), False, None, False, 150), ((35, 768), False, None, False, 140),
                    ((35, 670), False, None, False, 160), ((100, 572), False, None, False, 200), \
                    ((35, 474), False, None, False, 180), ((35, 380), True, None, False, None),
                    ((35, 278), False, None, False, 180), ((35, 180), False, None, False, 200), \
                    ((20, 20), False, None, True, None), ((180, 52), False, None, False, 220),
                    ((278, 52), True, None, False, None), ((376, 52), False, None, False, 220),
                    ((474, 52), True, None, False, 240), ((572, 100), False, None, False, 200), \
                    ((670, 52), False, None, False, 260), ((772, 52), False, None, False, 260),
                    ((870, 100), False, None, False, 150), ((968, 52), False, None, False, 280), \
                    ((1074, 15), False, None, True, None), ((1090, 180), False, None, False, 300),
                    ((1090, 278), False, None, False, 300), ((1090, 376), True, None, False, None),
                    ((1090, 474), False, None, False, 320), ((1060, 572), False, None, False, 200), \
                    ((1090, 670), True, None, False, None), ((1090, 768), False, None, False, 350),
                    ((1090, 866), False, 100, False, None), ((1090, 964), False, None, False, 400)]
    grids_pool = [Grid(a, b, c, d, e) for a, b, c, d, e in grids_tuples]
    for i in [2, 7, 17, 20, 33, 36]:
        grids_pool[i].name = 'Chance'
    grids_pool[0].name = 'Go'
    grids_pool[4].name = 'Income Tax'
    grids_pool[10].name = 'Prison Visiting'
    grids_pool[38].name = 'Luxury Tax'
    message_coors = [(210, 180), (210, 210), (210, 240), (210, 270), (210, 300)]

    # initialising
    pygame.init()
    clock = pygame.time.Clock()

    size = (1200, 1200)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Multidimensional_Monopoly')
    font = pygame.font.Font('/Library/Fonts/Arial Unicode.ttf', 25)
    black = (0, 0, 0)

    # initialize dimension
    change_dimension()

    # initialize images and adjust their sizes
    player1 = pygame.image.load('./figure/player1.png').convert_alpha()
    player2 = pygame.image.load('./figure/player2.png').convert_alpha()
    start_button = pygame.image.load('./images/start.png').convert_alpha()
    start_button = pygame.transform.scale(start_button, (100, 100))
    # end_button = pygame.image.load('./images/end.png').convert_alpha()
    # end_button = pygame.transform.scale(end_button, (90, 90))
    dice_button = pygame.image.load('./images/dice.png').convert_alpha()
    dice_button = pygame.transform.scale(dice_button, (80, 80))
    message_box = pygame.image.load('./images/message.png').convert_alpha()
    message_box = pygame.transform.scale(message_box, (550, 330))
    money = pygame.image.load('./images/money.png').convert_alpha()
    money = pygame.transform.scale(money, (70, 70))

    # initialize players and grids
    Player1 = Player('Player1', player1)
    Player2 = Player('Player2', player2)
    player_pool = [Player1, Player2]



    # surface rects
    dice_rect = dice_button.get_rect()
    dice_rect.left, dice_rect.top = 680, 200
    start_rect = start_button.get_rect()
    start_rect.left, start_rect.top = 800, 200
    # end_rect = end_button.get_rect()
    # end_rect.left, end_rect.top = 920, 200
    message_box_rect = message_box.get_rect()
    message_box_rect.left, message_box_rect.top = 130, 100
    money_rect = money.get_rect()
    money_rect.left, money_rect.top = 900, 180

    # variables initializing
    dice_point = 0
    active_player = None

    # parameters while running
    run = True
    button_alpha = 120
    game_start = False
    text_position = 0
    active_player = Player1
    while run:
        if not game_start:
            screen.blit(map, (0, 0))
            screen.blit(start_button, start_rect)
            screen.blit(message_box, message_box_rect)
            print_message('Press START to start the game!', (220, 180))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()  # quit game

                if event.type == pygame.MOUSEMOTION:

                    if start_rect.collidepoint(event.pos):
                        button_alpha = 255
                    else:
                        button_alpha = 120

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if start_rect.collidepoint(event.pos):  # 按下按钮
                        game_start = True
                        screen.blit(map, (0, 0))
                        print_message('Game started!', (220, 180))
                        screen.blit(message_box, message_box_rect)
                        screen.blit(dice_button, dice_rect)
                        # screen.blit(end_button, end_rect)
                        screen.blit(player1, Player1.location)
                        screen.blit(player2, Player2.location)
                        screen.blit(money, money_rect)
                        print_money()
                        print_message('Press the dice!', (220, 210))

            # screen.blit(dice_button, dice_rect)
            # screen.blit(start_button, start_rect)
            # screen.blit(test_pic, (0, 0))
            # blit_alpha(screen, start_button, start_rect, button_alpha)
            # blit_alpha(screen, test_pic, (0, 0), 100)

        if game_start:

            if active_player.pause:
                if active_player == Player1:
                    active_player = Player2
                    Player1.pause = False
                else:
                    active_player = Player1
                    Player2.pause = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if dice_rect.collidepoint(event.pos):
                        image_alpha = 255
                    else:
                        image_alpha = 190

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if dice_rect.collidepoint(event.pos):  # press the dice button
                        dice_point = random.randint(1, 6)
                        screen.blit(map, (0, 0))
                        # screen.blit(message_box, message_box_rect)
                        screen.blit(dice_button, dice_rect)
                        dice_point = random.randint(1, 6)
                        print_message(f'{active_player.name} has got a {dice_point}!')
                        move(active_player, dice_point)
                        pass_by(active_player)
                        screen.blit(money, money_rect)
                        print_money()
                        screen.blit(player1, Player1.location)
                        screen.blit(player2, Player2.location)
                        if active_player == Player1:
                            active_player = Player2
                        else:
                            active_player = Player1
                        lose(active_player)
                        text_position = 0

        pygame.display.flip()
        clock.tick(60)
