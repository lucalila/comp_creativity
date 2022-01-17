class Player(object):

    def __init__(self, name, figure):
        self.name = name
        self.money = 1000  # default money?
        self.location = (198, 255)  # coordinate of START needed
        self.properties = []  # necessary?
        self.pause = None  # bool
        self.round = 0
        self.figure = figure


class Grid(object):

    def __init__(self, coor, chance, stop, rent):
        # self.name = name  # necessary? name is already on the map
        self.coor = coor
        self.chance = chance  # Bool
        self.stop = stop  # Bool
        self.owner = None
        self.rent = rent  # for properties, stations and tax





