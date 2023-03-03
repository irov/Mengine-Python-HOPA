from Foundation.TaskManager import TaskManager
from HOPA.LeversPuzzleManager import LeversPuzzleManager


Enigma = Mengine.importEntity("Enigma")


class LeversPuzzle(Enigma):
    # ------------------------------------------------------------------------------------------------
    class Lever(object):
        def __init__(self, LeverID, MovieCheckBox):
            self.id = LeverID
            self.checkbox = MovieCheckBox

            self.checkbox.setEnable(True)
            self.checkbox.setValue(False)

        def getValue(self):
            return self.checkbox.getValue()

        def scopeClick(self, source):
            source.addListener(Notificator.onMovieCheckBox, Filter=(lambda o, v: o is self.checkbox))
            pass

    class Chip(object):
        def __init__(self, ChipID, MovieOff, MovieOn, StartState, WinState, LeverIDs):
            self.id = ChipID

            self.movie_on = MovieOn
            self.movie_off = MovieOff

            self.start_state = bool(StartState)
            self.win_state = bool(WinState)

            self.lever_ids = LeverIDs

            self.movie_on.setEnable(self.start_state)
            self.movie_off.setEnable(not self.start_state)

            self.movie_on.setLastFrame(False)
            self.movie_off.setLastFrame(False)

            self.state = self.start_state

        def skip(self):
            self.movie_on.setEnable(True)
            self.movie_off.setEnable(False)

            self.movie_on.setLastFrame(False)
            self.movie_off.setLastFrame(False)

        def changeState(self):
            self.state = not self.state

        def scopeSwitch(self, source):
            if self.state is True:
                source.addScope(self.scopeSwitchOn)
            else:
                source.addScope(self.scopeSwitchOff)

            source.addFunction(self.changeState)

        def scopeSwitchOn(self, source):
            source.addPlay(self.movie_on)
            source.addDisable(self.movie_on)

            source.addTask('TaskMovieRewind', Movie=self.movie_on)
            source.addEnable(self.movie_off)

        def scopeSwitchOff(self, source):
            source.addPlay(self.movie_off)
            source.addDisable(self.movie_off)

            source.addTask('TaskMovieRewind', Movie=self.movie_off)
            source.addEnable(self.movie_on)

        def isWinState(self):
            return self.state is self.win_state

    class ChipOver(object):
        def __init__(self, Chip_1, Chip_2, MovieOffOver, MovieOnOver):
            self.chip_1 = Chip_1
            self.chip_2 = Chip_2

            self.movie_off_over = MovieOffOver
            self.movie_on_over = MovieOnOver

            self.update()

        def skip(self):
            self.movie_on_over.setEnable(True)
            self.movie_off_over.setEnable(False)

            self.movie_on_over.setLastFrame(False)
            self.movie_off_over.setLastFrame(False)

        def update(self):
            if self.chip_1.state == self.chip_2.state:
                self.movie_on_over.setEnable(self.chip_1.state)
                self.movie_off_over.setEnable(not self.chip_1.state)
            else:
                self.movie_on_over.setEnable(False)
                self.movie_off_over.setEnable(True)

            self.movie_on_over.setLastFrame(False)
            self.movie_off_over.setLastFrame(False)

        def genScope(self, chips):
            if self.chip_1 in chips and self.chip_2 in chips:
                return self.scopeSwitchBoth
            elif self.chip_1 in chips:
                return self.scopeSwitchChip1
            elif self.chip_2 in chips:
                return self.scopeSwitchChip2
            else:
                return None

        def scopeSwitchBoth(self, source):
            if self.chip_1.state == self.chip_2.state:
                if self.chip_1.state is True:
                    with source.addParallelTask(3) as (tc_1, tc_2, tc_3):
                        tc_1.addScope(self.chip_1.scopeSwitch)
                        tc_2.addScope(self.chip_2.scopeSwitch)
                        tc_3.addPlay(self.movie_on_over)
                else:
                    with source.addParallelTask(3) as (tc_1, tc_2, tc_3):
                        tc_1.addScope(self.chip_1.scopeSwitch)
                        tc_2.addScope(self.chip_2.scopeSwitch)
                        tc_3.addPlay(self.movie_off_over)
            else:
                with source.addParallelTask(2) as (tc_1, tc_2):
                    tc_1.addScope(self.chip_1.scopeSwitch)
                    tc_2.addScope(self.chip_2.scopeSwitch)

            source.addFunction(self.update)

        def scopeSwitchChip1(self, source):
            if self.chip_1.state == self.chip_2.state:
                if self.chip_1.state is True:
                    with source.addParallelTask(2) as (tc_1, tc_2):
                        tc_1.addScope(self.chip_1.scopeSwitch)
                        tc_2.addPlay(self.movie_on_over)
                else:
                    source.addScope(self.chip_1.scopeSwitch)
            else:
                if self.chip_1.state is True:
                    source.addScope(self.chip_1.scopeSwitch)
                else:
                    with source.addParallelTask(2) as (tc_1, tc_2):
                        tc_1.addScope(self.chip_1.scopeSwitch)
                        tc_2.addPlay(self.movie_off_over)

            source.addFunction(self.update)

        def scopeSwitchChip2(self, source):
            if self.chip_2.state == self.chip_1.state:
                if self.chip_2.state is True:
                    with source.addParallelTask(2) as (tc_1, tc_2):
                        tc_1.addScope(self.chip_2.scopeSwitch)
                        tc_2.addPlay(self.movie_on_over)
                else:
                    source.addScope(self.chip_2.scopeSwitch)
            else:
                if self.chip_2.state is True:
                    source.addScope(self.chip_2.scopeSwitch)
                else:
                    with source.addParallelTask(2) as (tc_1, tc_2):
                        tc_1.addScope(self.chip_2.scopeSwitch)
                        tc_2.addPlay(self.movie_off_over)

            source.addFunction(self.update)

    # ------------------------------------------------------------------------------------------------

    def __init__(self):
        super(LeversPuzzle, self).__init__()

        self.param = None

        self.levers = {}
        self.chips = {}

        self.chips_over = []

    def load_data(self):
        self.param = LeversPuzzleManager.getParam(self.EnigmaName)

    def setup(self):
        levers = self.param.getLevers()
        for lever_id in levers:
            lever_chbox = levers[lever_id]
            self.levers[lever_id] = LeversPuzzle.Lever(lever_id, lever_chbox)

        chips = self.param.getChips()
        for chip_id in chips:
            movie_off, movie_on, state_start, state_win, lever_ids = chips[chip_id]

            chip = LeversPuzzle.Chip(chip_id, movie_off, movie_on, state_start, state_win, lever_ids)

            self.chips[chip_id] = chip

        chips_over = self.param.getChipsOver()
        for chip_id, chip_over_id, movie_off_over, movie_on_over in chips_over:
            chip_1 = self.chips.get(chip_id)
            chip_2 = self.chips.get(chip_over_id)

            chip_over = LeversPuzzle.ChipOver(chip_1, chip_2, movie_off_over, movie_on_over)

            self.chips_over.append(chip_over)
        pass

    def _onPreparation(self):
        super(LeversPuzzle, self)._onPreparation()
        self.load_data()
        self.setup()
        pass

    def scopeLeverSwitch(self, source, LeverHolder):
        for lever, source_race in source.addRaceTaskList(self.levers.itervalues()):
            with source_race.addParallelTask(2) as (SoundEffect, ChangeLeverState):
                SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'LeversPuzzle_ChangeLeverState')

                ChangeLeverState.addScope(lever.scopeClick)
            source_race.addFunction(LeverHolder.set, lever)
        pass

    def scopeLeverChange(self, source, LeverHolder):
        lever = LeverHolder.get()

        chips = []

        for chip in self.chips.itervalues():
            if lever.id not in chip.lever_ids:
                continue

            # or logic
            chips.append(chip)
        with source.addParallelTask(2) as (SoundEffect, MoveChip):
            MoveChip.addScope(self.scopeChipsChange, chips)
            SoundEffect.addNotify(Notificator.onSoundEffectOnObject, self.object, 'LeversPuzzle_MoveChip')

        # for chip, parallel in source.addParallelTaskList(chips):  #     parallel.addScope(chip.scopeSwitch)

    def scopeChipsChange(self, source, chips):
        if not chips:
            return

        scopes = []
        for chip_over in self.chips_over:
            scope = chip_over.genScope(chips)
            if scope is not None:
                scopes.append(scope)

        for scope, parallel in source.addParallelTaskList(scopes):
            parallel.addScope(scope)

    def _check_complete(self):
        for chip in self.chips.itervalues():
            if chip.isWinState() is False:
                return

        self.enigmaComplete()

    def _skipEnigmaScope(self, source):
        chips = []
        for chip in self.chips.itervalues():
            if chip.state is False:
                chips.append(chip)
        source.addScope(self.scopeChipsChange, chips)

    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self._clean_resources()

        self.load_data()
        self.setup()
        self._playEnigma()
        pass

    def _playEnigma(self):
        LeverHolder = Holder()

        with TaskManager.createTaskChain(Name="LeversPuzzle", Repeat=True) as tc:
            tc.addScope(self.scopeLeverSwitch, LeverHolder)
            tc.addScope(self.scopeLeverChange, LeverHolder)
            tc.addFunction(self._check_complete)

    def _clean_resources(self):
        TaskManager.cancelTaskChain("LeversPuzzle", exist=False)

        self.param = None

        self.levers = {}
        self.chips = {}

        self.chips_over = []

    def _onFinalize(self):
        super(LeversPuzzle, self)._onFinalize()

        self._clean_resources()
