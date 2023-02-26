from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.TicTacToeManager import TicTacToeManager

from CellPlate import CellPlate

ALIAS_ENV = ""

ALIAS_GAME_TEXT = "$AliasTicTacToeCurrentPlayer"
# game_text aliases texts:
TEXT_DRAW = "ID_TEXT_DRAW_TICTACTOE"
TEXT_WELCOME = "ID_TEXT_WELCOME_TICTACTOE"  # text args: x_player_name, o_player_name
TEXT_WON = "ID_TEXT_WON_TICTACTOE"  # text args: player_name
TEXT_MOVE = "ID_TEXT_MOVE_TICTACTOE"  # text args: player_name

ALIAS_STATS_X = "$AliasTicTacToeXStats"
ALIAS_STATS_O = "$AliasTicTacToeOStats"
# alias_stats_x and alias stats_o should use text_stats but with proper text args
TEXT_STATS = "ID_TEXT_STATS_TICTACTOE"  # text args: player_name, player_wins

CELL_NUMBER = 9

class TicTacToe(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "CurrentPlayer")
        Type.addActionActivate(Type, "Winner")
        Type.addActionActivate(Type, "PlayerXWins")
        Type.addActionActivate(Type, "PlayerOWins")
        Type.addActionActivate(Type, "CellsState")

    def __init__(self):
        super(TicTacToe, self).__init__()
        self.tc = None
        self.content = None
        self.reset_button = None
        self.transition_button = None
        self.cell_plates = {}
        # this two below better change for self.x_player_params = None
        self.x_player_name = ''
        self.o_player_name = ''

    def _onPreparation(self):
        self.content = self.object.getObject('Movie2_Content')
        self.reset_button = self.object.getObject('Movie2Button_Reset')
        self.transition_button = self.object.getObject('Movie2Button_Transition')

        # LOADING PLAYERS NAMES FROM PLAYERS PARAMS RECEIVED FROM MANAGER
        x_player_params = TicTacToeManager.getPlayerParams('X')
        o_player_params = TicTacToeManager.getPlayerParams('O')
        self.x_player_name = x_player_params.player_name
        self.o_player_name = o_player_params.player_name

        # bind button reset on content slot
        slot_reset = self.content.getMovieSlot('reset')
        entity_node_reset_button = self.reset_button.getEntityNode()
        slot_reset.addChild(entity_node_reset_button)

        # bind button transition on content transition slot
        slot_transition = self.content.getMovieSlot('transition')
        entity_node_transition_button = self.transition_button.getEntityNode()
        slot_transition.addChild(entity_node_transition_button)

        # setting up scene texts states to default
        self.__setText(ALIAS_GAME_TEXT, TEXT_WELCOME, self.x_player_name, self.o_player_name)
        self.__setText(ALIAS_STATS_X, TEXT_STATS, self.x_player_name, self.object.getParam('PlayerXWins'))
        self.__setText(ALIAS_STATS_O, TEXT_STATS, self.o_player_name, self.object.getParam('PlayerOWins'))

        # creating cell plates using cell prototypes
        # binding them to slots in content
        # and saving cell plates in dict: self.cell_plates
        for i in range(CELL_NUMBER):
            slot = self.content.getMovieSlot('cell_{}'.format(i))
            plate = self.__createCellPlate(slot, i)
            self.cell_plates[i] = plate

        # restoring CellState Params
        self.__restoreCellStates()

    def __restoreCellStates(self):
        """
        Restoring cells states from params cells_states{}
        """

        cells_state_dict = self.object.getParam('CellsState')

        for i in range(CELL_NUMBER):
            cell_key = 'cell_{}'.format(i)
            cell_state = cells_state_dict.get(cell_key, None)

            if cell_state is not None:
                self.cell_plates[i].state = cell_state  # restoring CellPlate.state
                self.cell_plates[i].restoreMovieState()  # enable correct movie_cell

    def __createCellPlate(self, slot, id_):
        movie_cell_plate = self.object.tryGenerateObjectUnique('cell_{}'.format(id_), 'Movie2_CellPlate', Enable=True)
        movie_cell_plate_entity_node = movie_cell_plate.getEntityNode()
        slot.addChild(movie_cell_plate_entity_node)

        cell_plate_state_slot = movie_cell_plate.getMovieSlot('cell_state')
        movie_cell_x = self.object.tryGenerateObjectUnique('cell_state_x_{}'.format(id_), 'Movie2_CellState_X', Enable=False)
        movie_cell_o = self.object.tryGenerateObjectUnique('cell_state_o_{}'.format(id_), 'Movie2_CellState_O', Enable=False)

        cell_x_entity_node = movie_cell_x.getEntityNode()
        cell_o_entity_node = movie_cell_o.getEntityNode()

        cell_plate_state_slot.addChild(cell_x_entity_node)
        cell_plate_state_slot.addChild(cell_o_entity_node)

        cell_plate = CellPlate(id_, movie_cell_plate, movie_cell_x, movie_cell_o)

        return cell_plate

    def _onActivate(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        self.tc_cells_race = TaskManager.createTaskChain(Repeat=True)
        self._runTaskChain()

    def __resetButtonActivate(self):
        self.object.setParam('CurrentPlayer', 'X')  # reset first player to default
        self.object.setParam('Winner', None)  # reset winner
        self.object.setParam('CellsState', {})  # !!!!! clear CellsState Params

        # change game text alias to default
        self.__setText(ALIAS_GAME_TEXT, TEXT_WELCOME, self.x_player_name, self.o_player_name)

        # reseting cells
        for cell_plate in self.cell_plates.itervalues():
            cell_plate.clearMovieState()

    def __setText(self, alias, text_id, *args):
        Mengine.setTextAlias(ALIAS_ENV, alias, text_id)
        if args:
            Mengine.setTextAliasArguments(ALIAS_ENV, alias, *args)

    def __findWinner(self):
        board_size = 3

        cells_state_list = []
        for cell_plate in self.cell_plates.itervalues():
            cells_state_list.append(cell_plate.state)

        def check_cells_state_set(cells):
            # print cells
            def check_equal(iterator):
                iterator = iter(iterator)
                try:
                    first = next(iterator)
                except StopIteration:
                    return True
                return all(first == rest for rest in iterator)

            if cells[0] is not None and check_equal(cells):
                return cells[0]
            else:
                return None

        # Checking rows
        for i in range(board_size):
            cells_state_set = []
            for j in range(board_size):
                cells_state_set.append(cells_state_list[i * board_size + j])
            rc = check_cells_state_set(cells_state_set)
            if rc is not None:
                return rc

        # Checking columns
        for i in range(board_size):
            cells_state_set = []
            for j in range(board_size):
                cells_state_set.append(cells_state_list[i + board_size * j])
            rc = check_cells_state_set(cells_state_set)
            if rc is not None:
                return rc

        # Checking upper left to down right diagonal
        cells_state_set = []
        for i in range(board_size):
            cells_state_set.append(cells_state_list[i * (board_size + 1)])
        rc = check_cells_state_set(cells_state_set)
        if rc is not None:
            return rc

        # Checking upper right to down left diagonal
        cells_state_set = []
        for i in range(board_size):
            cells_state_set.append(cells_state_list[(board_size - 1) * (i + 1)])
        rc = check_cells_state_set(cells_state_set)
        if rc is not None:
            return rc

        # if no winner yet and board is full, return 'draw'
        # else mean board is not full and no winner, return None
        if None not in cells_state_list:
            return 'draw'
        else:
            return None

    def __updatePlayerStats(self, winner):
        self.object.getParam('PlayerXWins')
        self.object.getParam('PlayerOWins')

        if winner == 'X':
            self.object.setParam('PlayerXWins', self.PlayerXWins + 1)
            self.__setText(ALIAS_STATS_X, TEXT_STATS, self.x_player_name, self.object.getParam('PlayerXWins'))

        elif winner == 'O':
            self.object.setParam('PlayerOWins', self.PlayerOWins + 1)
            self.__setText(ALIAS_STATS_O, TEXT_STATS, self.o_player_name, self.object.getParam('PlayerXWins'))  # if draw do nothing

    def __updateWinner(self):
        winner = self.__findWinner()

        if winner is not None:
            self.object.setParam('Winner', winner)

            if self.object.getParam('Winner') == 'X':
                self.__setText(ALIAS_GAME_TEXT, TEXT_WON, self.x_player_name)
            elif self.Winner == 'O':
                self.__setText(ALIAS_GAME_TEXT, TEXT_WON, self.o_player_name)
            elif self.Winner == 'draw':
                self.__setText(ALIAS_GAME_TEXT, TEXT_DRAW)
            self.__updatePlayerStats(winner)

    def __updateCurrentPlayer(self):
        if self.object.getParam('CurrentPlayer') == 'X':
            self.object.setParam('CurrentPlayer', 'O')
            self.__setText(ALIAS_GAME_TEXT, TEXT_MOVE, self.o_player_name)
        elif self.CurrentPlayer == 'O':
            self.object.setParam('CurrentPlayer', 'X')
            self.__setText(ALIAS_GAME_TEXT, TEXT_MOVE, self.x_player_name)

    def __setParamCellsState(self, cell_id):
        """
        update CellsState dict in orm
        """
        cell_state = self.object.getParam('CurrentPlayer')
        cells_state = self.object.getParam('CellsState')  # pull dict from orm

        cell_key = 'cell_{}'.format(cell_id)  # setting up CellsState dict key
        cells_state[cell_key] = cell_state  # add new key:value pair

        self.object.setParam('CellsState', cells_state)  # replace db dict with local one

    def __resolveClickOnCell(self, cell_plate):
        if cell_plate is None:
            return

        if cell_plate.state is not None:
            return

        cell_plate.setMovieState()
        self.__setParamCellsState(cell_plate.plate_id)  # !!!!! Saving CellsState params
        self.__updateCurrentPlayer()
        self.__updateWinner()

    def __playerChangeNotify(self, scope):
        scope.addNotify(Notificator.onTicTacToePlayerChange, self.object.getParam('CurrentPlayer'))

    def _runTaskChain(self):
        with self.tc as tc:
            with tc.addRaceTask(2) as (reset, transit):
                reset.addTask('TaskMovie2ButtonClick', Movie2Button=self.reset_button)
                reset.addFunction(self.__resetButtonActivate)

                transit.addTask('TaskMovie2ButtonClick', Movie2Button=self.transition_button)
                transit.addNotify(Notificator.onTicTacToeSceneTransition, 'Menu')

        with self.tc_cells_race as tc_cells_race:
            for (id_, cell), source_race in tc_cells_race.addRaceTaskList(self.cell_plates.iteritems()):
                source_race.addTask('TaskMovie2SocketClick', Movie2=cell.movie_plate, SocketName='cell')
                source_race.addFunction(self.__resolveClickOnCell, cell)

                source_race.addTask('TaskScope', Scope=self.__playerChangeNotify)

    def _onDeactivate(self):
        self._cleanUp()

    def _cleanUp(self):
        # remove from parent and destroy movie_plate, state_x and state_o movies from cell_plate
        for cell_plate in self.cell_plates.itervalues():
            cell_plate.cleanUp()

        entity_node_reset_button = self.reset_button.getEntityNode()
        entity_node_reset_button.removeFromParent()

        entity_node_transition_button = self.transition_button.getEntityNode()
        entity_node_transition_button.removeFromParent()

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        if self.tc_cells_race is not None:
            self.tc_cells_race.cancel()
            self.tc_cells_race = None