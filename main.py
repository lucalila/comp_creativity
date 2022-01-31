import json
import pygame
import random
import sys
from pygame import QUIT
from dimension import Dimension
from create_map import create_a_map

load_from_save = False  # True for loading dimensions from saved json file


class Player(object):

    def __init__(self, name, figure):
        self.name = name
        self.money = 2000  # default money
        self.location = (688, 688)  # coordinate of GO
        self.pause = None  # bool
        self.round_count = 0
        self.figure = figure


class Grid(object):

    def __init__(self, coor, chance, pay, stop, rent):
        self.name = None  # necessary? name is already on the map
        self.coor = coor
        self.chance = chance  # Bool
        self.tax = pay
        self.stop = stop  # Bool
        self.owner = None
        self.rent = rent  # for properties, stations and tax


def change_dimension():
    global locations
    global action_cards
    global map_path
    global map
    global topic
    global load_from_save
    screen.blit(map_basic, (0, 0))
    print_message('Loading new dimension...', text_font, message_coors[0])
    pygame.display.flip()

    if not load_from_save:
        dimension = Dimension()
        dimension.change_topic()
        dimension.generate_locations()
        dimension.generate_action_cards()
        locations = dimension.locations
        action_cards = dimension.action_cards
        topic = dimension.topic
        map_path = create_a_map(locations, topic)
        map = pygame.image.load(map_path).convert_alpha()
        # change Grids name
        grids_to_be_changed = [6, 8, 9, 11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29, 31, 32, 34, 37, 39, 1, 3, 12,
                               28, 5,
                               15, 25, 35, 30, 20]
        for i in range(0, 30):
            grids_pool[grids_to_be_changed[i]].name = locations[i + 1]

    # live samples from saved dimensions
    else:
        dimension = saved_dimensions[str(dimension_count)]
        locations = dimension['locations']
        action_cards = dimension['action_cards']
        topic = dimension['topic']
        map_path = create_a_map(locations, topic)
        map = pygame.image.load(map_path).convert_alpha()
        # change Grids name
        grids_to_be_changed = [6, 8, 9, 11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29, 31, 32, 34, 37, 39, 1, 3, 12,
                               28, 5,
                               15, 25, 35, 30, 20]
        for i in range(0, 30):
            grids_pool[grids_to_be_changed[i]].name = locations[i + 1]


def ask_the_player():
    global text_position
    text_position = 0
    screen.blit(map, (0, 0))
    screen.blit(accept, accept_rect)
    screen.blit(cancel, cancel_rect)
    print_message('You have already changed 5 dimensions!', text_font)
    print_message('Click the green button to continue the game.', text_font)
    print_message('Click the red button to end the game.', text_font)
    text_position = 0
    pygame.display.flip()
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if accept_rect.collidepoint(event.pos):
                    loop = False
                elif cancel_rect.collidepoint(event.pos):
                    loop = False
                    pygame.quit()
                    sys.exit()


def print_money():
    player1_money = f'{Player1.name}: {Player1.money}'
    player2_money = f'{Player2.name}: {Player2.money}'
    print_message(player1_money, text_font, (500, 270))
    print_message(player2_money, text_font, (500, 300))


def take_an_action(player, action_tuple):
    global money
    if action_tuple[2]:
        for grid in grids_pool:
            if action_tuple[2] == grid.name:
                target_grid = grid
                player.location = target_grid.coor
                player.round_count = grids_pool.index(target_grid)
                if target_grid.owner is None and target_grid.rent:
                    print_message(f'The {target_grid.name} now belongs to {player.name}!', text_font)
                    target_grid.owner = player.name
                    player.money -= target_grid.rent
    if action_tuple[1] in ['positiv', 'neutral'] and action_tuple[3]:
        player.money += int(action_tuple[3])
    if action_tuple[1] == 'negativ' and action_tuple[3]:
        player.money -= int(action_tuple[3])
    screen.blit(map, (0, 0))
    screen.blit(dice_button, dice_rect)


def lose(player):
    global text_position, game_start
    text_position = 0
    if player.money <= 0:
        screen.blit(map, (0, 0))
        screen.blit(accept, accept_rect)
        screen.blit(cancel, cancel_rect)
        print_message(f'{player.name} does not have money any more! ', text_font)
        for p in player_pool:
            if player != p:
                print_message(f'{p.name} has won!', text_font)
        print_message('Click the green button to restart the game.', text_font)
        print_message('Click the red button to end the game.', text_font)
        text_position = 0
        pygame.display.flip()
        loop = True
        while loop:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if accept_rect.collidepoint(event.pos):
                        loop = False
                        screen.blit(map_basic, (0, 0))
                        for player in player_pool:
                            player.money = 2000
                            player.location = (688, 688)
                            player.round_count = 0
                            game_start = False
                        for grid in grids_pool:
                            grid.owner = None

                    elif cancel_rect.collidepoint(event.pos):
                        loop = False
                        pygame.quit()
                        sys.exit()


# rules functions
def move(player, point):
    global dimension_count
    global text_position
    player.round_count += point
    if player.round_count >= 39:  # sum of grids
        player.round_count -= 39
        if player == Player1:
            dimension_count += 1
            if dimension_count == 6:
                text_position = 0
                ask_the_player()
                screen.blit(map, (0, 0))
                screen.blit(dice_button, dice_rect)
            change_dimension()
            screen.blit(map, (0, 0))
            print_message('Dimension has now changed to ' + topic + ' !', text_font)
            screen.blit(dice_button, dice_rect)
            screen.blit(money, money_rect)
            print_money()
            screen.blit(player1, Player1.location)
            screen.blit(player2, Player2.location)
        print_message(f'Over start, {player} have got 200 Euro.', text_font)
        player.money += 200
    player.location = grids_pool[player.round_count].coor


def print_message(text, font, position=None):
    if len(text) > 46:
        if len(text) > 92:
            texts = [text[:47] + '-', text[47:92] + '-', text[92:]]
        else:
            texts = [text[:47] + '-', text[47:]]
    else:
        texts = [text]
    for text in texts:
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
    global text_position
    for grid in grids_pool:
        if player.location == grid.coor:
            active_grid = grid
    print_message(f'{player.name} is now at {active_grid.name}!', text_font)
    if active_grid.chance:
        text_position = 0
        chance = random.choice(action_cards)
        chance_text = chance[0]
        screen.blit(map, (0, 0))
        screen.blit(accept, accept_rect)
        print_message(f'{player.name} is now at CHANCE!', text_font)
        print_message(">>>" + chance_text, text_font)
        print_message('Click the ACCEPT button to take an action!', text_font)
        screen.blit(player1, Player1.location)
        screen.blit(player2, Player2.location)
        pygame.display.flip()
        loop = True
        while loop:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if accept_rect.collidepoint(event.pos):
                        take_an_action(player, chance)
                        loop = False

    elif active_grid.tax:
        print_message(f'{player.name} should pay {active_grid.tax} Euro for {active_grid.name}.',
                      text_font)
        player.money -= active_grid.tax

    elif active_grid.owner:
        print_message(f'{player.name} should pay {active_grid.owner} {active_grid.rent} Euro.',
                      text_font)
        player.money -= active_grid.rent
        for p in player_pool:
            if player != p:
                p.money += active_grid.rent

    elif active_grid.stop:
        print_message(f'{player.name} should take a break.', text_font)
        player.pause = True
        if active_grid.coor == (1074, 15):
            player.round = 10
            player.location = (30, 1100)

    elif active_grid.owner is None and active_grid.rent:
        print_message(f'The {active_grid.name} now belongs to {player.name}!', text_font)
        active_grid.owner = player.name
        player.money -= active_grid.rent


if __name__ == '__main__':
    # grids data
    grids_tuples = [((687, 687), False, None, False, None), ((600, 685), False, None, False, 60),
                    ((544, 685), True, None, False, None), ((482, 685), False, None, False, 60),
                    ((418, 685), False, 200, False, None), ((357, 656), False, None, False, 200), \
                    ((296, 685), False, None, False, 100), ((235, 685), True, None, False, None),
                    ((173, 685), False, None, False, 100), ((112, 685), False, None, False, 120), \
                    ((18, 687), False, None, False, None), ((22, 602), False, None, False, 140),
                    ((22, 541), False, None, False, 150), ((22, 480), False, None, False, 140),
                    ((22, 418), False, None, False, 160), ((62, 357), False, None, False, 200), \
                    ((22, 296), False, None, False, 180), ((22, 237), True, None, False, None),
                    ((22, 173), False, None, False, 180), ((22, 112), False, None, False, 200), \
                    ((12, 12), False, None, True, None), ((112, 32), False, None, False, 220),
                    ((173, 32), True, None, False, None), ((235, 32), False, None, False, 220),
                    ((296, 32), True, None, False, 240), ((357, 62), False, None, False, 200), \
                    ((418, 32), False, None, False, 260), ((482, 32), False, None, False, 260),
                    ((543, 32), False, None, False, 150), ((605, 32), False, None, False, 280), \
                    ((671, 32), False, None, True, None), ((680, 112), False, None, False, 300),
                    ((680, 173), False, None, False, 300), ((680, 235), True, None, False, None),
                    ((680, 296), False, None, False, 320), ((680, 357), False, None, False, 200), \
                    ((680, 418), True, None, False, None), ((680, 480), False, None, False, 350),
                    ((680, 541), False, 100, False, None), ((680, 602), False, None, False, 400)]
    grids_pool = [Grid(a, b, c, d, e) for a, b, c, d, e in grids_tuples]
    for i in [2, 7, 17, 20, 33, 36]:
        grids_pool[i].name = 'Chance'
        grids_pool[0].name = 'Start'
        grids_pool[4].name = 'Income Tax'
        grids_pool[10].name = 'Prison Visiting'
        grids_pool[38].name = 'Luxury Tax'
        message_coors = [(110, 110), (110, 140), (110, 170), (110, 200), (110, 230)]

    # initialising pagame
    pygame.init()
    clock = pygame.time.Clock()
    size = (750, 750)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Multidimensional_Monopoly')
    welcome_font = font = pygame.font.Font('./fonts/welcome.otf', 30)
    text_font = pygame.font.Font('./fonts/text.otf', 28)
    black = (0, 0, 0)

    # initialize images and adjust their sizes
    map_basic = pygame.image.load('./images/map_base.JPG').convert()
    map_basic = pygame.transform.scale(map_basic, (750, 750))
    map = pygame.image.load('./images/map_base.JPG').convert()
    map = pygame.transform.scale(map, (750, 750))
    player1 = pygame.image.load('./images/boy.png').convert_alpha()
    player2 = pygame.image.load('./images/girl.png').convert_alpha()
    start_button = pygame.image.load('./images/start.png').convert_alpha()
    start_button = pygame.transform.scale(start_button, (100, 100))
    cancel = pygame.image.load('./images/cancel.png').convert_alpha()
    cancel = pygame.transform.scale(cancel, (70, 70))
    dice_button = pygame.image.load('./images/dice.png').convert_alpha()
    dice_button = pygame.transform.scale(dice_button, (70, 70))
    accept = pygame.image.load('./images/accept.png').convert_alpha()
    accept = pygame.transform.scale(accept, (70, 70))
    money = pygame.image.load('./images/money.png').convert_alpha()
    money = pygame.transform.scale(money, (70, 70))

    # initialize saved dimensions
    with open('./dimensions_file.json', 'r', encoding='utf-8') as d:
        saved_dimensions = json.load(d)

    # initialize players and grids
    Player1 = Player('Player1', player1)
    Player2 = Player('Player2', player2)
    player_pool = [Player1, Player2]

    # surface rects
    dice_rect = dice_button.get_rect()
    dice_rect.left, dice_rect.top = 120, 260
    start_rect = start_button.get_rect()
    start_rect.left, start_rect.top = 320, 300
    cancel_rect = cancel.get_rect()
    cancel_rect.left, cancel_rect.top = 290, 260
    accept_rect = accept.get_rect()
    accept_rect.left, accept_rect.top = 200, 260
    money_rect = money.get_rect()
    money_rect.left, money_rect.top = 420, 260

    # variables initializing
    dice_point = 0
    active_player = Player1
    locations = list()
    action_cards = list()
    map_path = None
    topic = None
    map = None
    dimension_count = 1

    # parameters while running
    run = True
    game_start = False
    text_position = 0

    while run:
        if not game_start:
            screen.blit(map_basic, (0, 0))
            screen.blit(start_button, start_rect)
            print_message('Welcome to multidimensional monopoly!', welcome_font, (120, 220))
            print_message('Press START to start the game!', welcome_font, (170, 260))

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()  # quit game

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if start_rect.collidepoint(event.pos):  # 按下按钮
                        game_start = True
                        if dimension_count == 1:
                            change_dimension()
                        screen.blit(map, (0, 0))
                        print_message('Game started!', text_font, (110, 110))
                        screen.blit(dice_button, dice_rect)
                        screen.blit(player1, Player1.location)
                        screen.blit(player2, Player2.location)
                        screen.blit(money, money_rect)
                        print_money()
                        print_message('Press the dice!', text_font, (110, 140))

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
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if dice_rect.collidepoint(event.pos):  # press the dice button
                        screen.blit(map, (0, 0))
                        screen.blit(dice_button, dice_rect)
                        dice_point = random.randint(1, 6)
                        print_message(f'{active_player.name} has got a {dice_point}!', text_font)
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
