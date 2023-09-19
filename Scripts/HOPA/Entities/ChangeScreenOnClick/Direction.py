class Direction(object):
    Up = 0
    Left = 1
    Right = 2
    Down = 3

    @staticmethod
    def get(number):
        return abs(number % 4)

    @staticmethod
    def getReverted(number):
        return abs((4 - number) % 4)
