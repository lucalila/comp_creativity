class Player(object):

    def __init__(self, name, figure):
        self.name = name
        self.money = 2000  # default money?
        self.location = (1100, 1100)  # coordinate of START needed
        self.properties = []  # necessary?
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





