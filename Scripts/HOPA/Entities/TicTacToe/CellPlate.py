from Foundation.DemonManager import DemonManager

class CellPlate(object):
    def __init__(self, plate_id, movie_plate, movie_cell_x, movie_cell_o):
        self.plate_id = plate_id
        self.movie_plate = movie_plate
        self.movie_cell_x = movie_cell_x
        self.movie_cell_o = movie_cell_o
        self.state = None

    def setMovieState(self, current_player=None):
        demon_tictactoe = DemonManager.getDemon('TicTacToe')

        if current_player is None:
            current_player = demon_tictactoe.getParam('CurrentPlayer')

        if current_player == 'X':
            self.movie_cell_x.setEnable(True)
        elif current_player == 'O':
            self.movie_cell_o.setEnable(True)
        else:
            Trace.log("Manager", 0, "[CellPlate]incorrect current_player")

        self.state = current_player

    def restoreMovieState(self):
        if self.state == 'X':
            self.movie_cell_x.setEnable(True)
        elif self.state == 'O':
            self.movie_cell_o.setEnable(True)

    def clearMovieState(self):
        if self.state == 'X':
            self.movie_cell_x.setEnable(False)
        elif self.state == 'O':
            self.movie_cell_o.setEnable(False)
        self.state = None  # print 'clearMovieState call: reseted state for plate_id = {}'.format(self.plate_id)

    def cleanUp(self):
        for obj in [self.movie_cell_x, self.movie_cell_o, self.movie_plate]:
            if obj is None:
                continue
            obj_node = obj.getEntityNode()
            obj_node.removeFromParent()

            obj.onDestroy()