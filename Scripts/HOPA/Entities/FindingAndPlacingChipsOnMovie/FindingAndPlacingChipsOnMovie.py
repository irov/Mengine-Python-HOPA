from Foundation.ArrowManager import ArrowManager
from Foundation.TaskManager import TaskManager
from HOPA.FindingAndPlacingChipsOnMovieManager import FindingAndPlacingChipsOnMovieManager

Enigma = Mengine.importEntity("Enigma")

class Chip(object):
    def __init__(self, chip_id, chip_movie, movie_place, demon_node):
        self.chip_id = chip_id
        self.chip_movie = chip_movie
        self.movie_place = movie_place
        self.demon_node = demon_node

    def cleanUp(self):
        self.chip_movie.setEnable(False)
        self.movie_place.setEnable(False)
        self.demon_node.addChild(self.chip_movie.getEntityNode())
        self.demon_node.addChild(self.movie_place.getEntityNode())

class FindingAndPlacingChipsOnMovie(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "RemainingChips")
        pass

    def __init__(self):
        super(FindingAndPlacingChipsOnMovie, self).__init__()
        self.current_chip = None
        self.tc = None
        self.arrow = ArrowManager.getArrow()
        self.chips = {}

    def _onPreparation(self):
        super(FindingAndPlacingChipsOnMovie, self)._onPreparation()
        self.__loadParam()

    def _onActivate(self):
        super(FindingAndPlacingChipsOnMovie, self)._onActivate()

    def _onDeactivate(self):
        super(FindingAndPlacingChipsOnMovie, self)._onDeactivate()
        self.__cleanUp()

    def __loadParam(self):
        self.params = FindingAndPlacingChipsOnMovieManager.getParams(self.EnigmaName)

    def __setup(self):
        if self.params is None:
            return
        self.content = self.object.getObject('Movie2_MGContent')

        for chip_param in self.params.values():
            if chip_param.chip_id not in self.RemainingChips:
                continue
            chip_movie = self.object.getObject(chip_param.chip_movie_name)
            movie_place = self.object.getObject(chip_param.movie_place_name)
            movie_place.setEnable(True)
            if not self.content.hasSlot(chip_param.place_slot):
                error_message = 'FindingAndPlacingChipsOnMovie.__setup Movie2_MGContent doesnt has slot {} for {}'.format(chip_param.place_slot, chip_param.chip_id)
                Trace.log("Manager", 0, error_message)

            slot = self.content.getMovieSlot(chip_param.place_slot)
            slot.addChild(movie_place.getEntityNode())
            chip = Chip(chip_param.chip_id, chip_movie, movie_place, self.object.getEntityNode())
            self.chips[chip.chip_id] = chip

    def __createParam(self):
        if len(self.RemainingChips) != 0:
            return

        self.object.setParam('RemainingChips', self.params.keys())

    def _playEnigma(self):
        self.__createParam()
        self.__setup()
        self.__setNewCurrentChip()
        self.__runTaskChain()

    def _restoreEnigma(self):
        self.__setup()
        self.__setNewCurrentChip()
        self.__runTaskChain()

    def _resetEnigma(self):
        self.__cleanUp()
        self._playEnigma()

    def _skipEnigmaScope(self, skip_source):
        if self.current_chip is not None:
            skip_source.addDisable(self.current_chip.chip_movie)

        for (chip, parallel) in skip_source.addParallelTaskList(self.chips.values()):
            if chip.movie_place.getEnable() is False:
                parallel.addDummy()
            else:
                parallel.addPlay(chip.movie_place, Wait=True, Loop=False)
                parallel.addFunction(chip.cleanUp)
                parallel.addFunction(self.object.delParam, 'RemainingChips', chip.chip_id)

    def __runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            tc.addFunction(self.__prepareChip)
            tc.addScope(self.__scopeChipStart)
            tc.addFunction(self.__setNewCurrentChip)

    def __prepareChip(self):
        self.arrow.addChild(self.current_chip.chip_movie.getEntityNode())
        self.current_chip.chip_movie.setEnable(True)

    def __scopeChipStart(self, source):
        current_movie_place = self.current_chip.movie_place

        with source.addRepeatTask() as (source_repeat, source_until):
            source_repeat.addTask('TaskMovie2SocketEnter', Movie2=current_movie_place, SocketName='socket')
            source_repeat.addFunction(self.__setSelectChip, self.current_chip, True)

            source_repeat.addTask('TaskMovie2SocketLeave', Movie2=current_movie_place, SocketName='socket')
            source_repeat.addFunction(self.__setSelectChip, self.current_chip, False)

            source_until.addTask('TaskMovie2SocketClick', Movie2=current_movie_place, SocketName='socket')
            source_until.addScope(self.__scopeResolveClick)

    def __setSelectChip(self, chip, value):
        chip_movie = chip.chip_movie
        if value is True:
            if 'enter' in chip_movie.getParam('DisableLayers'):
                chip_movie.delParam('DisableLayers', 'enter')

            if 'idle' not in chip_movie.getParam('DisableLayers'):
                chip_movie.appendParam('DisableLayers', 'idle')

        elif value is False:
            if 'idle' in chip_movie.getParam('DisableLayers'):
                chip_movie.delParam('DisableLayers', 'idle')

            if 'enter' not in chip_movie.getParam('DisableLayers'):
                chip_movie.appendParam('DisableLayers', 'enter')

    def __scopeResolveClick(self, source):
        source.addDisable(self.current_chip.chip_movie)
        source.addPlay(self.current_chip.movie_place, Wait=True, Loop=False)
        source.addDisable(self.current_chip.movie_place)
        source.addFunction(self.object.delParam, 'RemainingChips', self.current_chip.chip_id)

    def __setNewCurrentChip(self):
        if self.current_chip is not None:
            self.current_chip.cleanUp()
        if len(self.RemainingChips) == 0:
            self.tc.setRepeat(False)
            self.enigmaComplete()
            return

        self.current_chip = self.chips.get(self.RemainingChips[0])

    def __cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        for chip in self.chips.values():
            chip.cleanUp()