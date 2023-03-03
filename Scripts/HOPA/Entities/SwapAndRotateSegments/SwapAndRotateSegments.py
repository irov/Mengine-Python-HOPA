import math

from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.SwapAndRotateSegmentsManager import SwapAndRotateSegmentsManager


Enigma = Mengine.importEntity("Enigma")


class Chip(object):
    def __init__(self, chip_id, movie, start_position, finish_position, numbers_of_chips, slot):
        self.id = chip_id
        self.movie = movie
        self.node = movie.getEntityNode()
        self.slot = slot
        self.startPosition = start_position
        self.finishPosition = finish_position
        self.currentPosition = 1
        self.isSelected = False
        self.numOfChips = numbers_of_chips
        rotate_angle_degree = 360 / numbers_of_chips
        self.rotateAngle = rotate_angle_degree * math.pi / 180
        self.set_select(False)
        self.currentAngle = 0
        slot.addChild(self.node)

    def set_select(self, flag):
        if flag is True:
            if 'Select' in self.movie.getParam('DisableLayers'):
                self.movie.delParam('DisableLayers', 'Select')
        elif flag is False:
            self.movie.appendParam('DisableLayers', 'Select')
        self.isSelected = flag

    def set_current_position(self, position):
        self.currentPosition = position

    def rotate_to(self, source, position_to):
        angle_to = self.calculate_rotate_angle(position_to)
        self.currentAngle -= angle_to
        rotate_time = DefaultManager.getDefaultFloat('SwapAndRotateSegmentsRotateTime', 500.0)
        source.addTask('TaskNodeRotateTo', Node=self.slot, To=self.currentAngle, Time=rotate_time)
        source.addFunction(self.set_current_position, position_to)

    def calculate_rotate_angle(self, position_to):
        position_from = self.currentPosition
        difference = (position_to - position_from) % self.numOfChips
        angle = difference * self.rotateAngle
        return angle


class SwapAndRotateSegments(Enigma):
    def __init__(self):
        super(SwapAndRotateSegments, self).__init__()
        self.param = None
        self.tc = None
        self.Chips = {}
        self.selected_chip = None

    # -------------- Preparation ---------------------------------------------------------------------------------------
    def clean_up(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        for chip in self.Chips.values():
            chip.node.removeFromParent()

    def load_param(self):
        self.param = SwapAndRotateSegmentsManager.getParam(self.EnigmaName)

    def setup(self):
        if self.param is None:
            msg = "Enigma {}: self.param is None on setup stage".format(self.EnigmaName)
            Trace.log("Entity", 0, msg)
            return

        group_name = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        group = GroupManager.getGroup(group_name)

        numbers_of_chips = len(self.param.ChipsParam)
        self.BG = group.getObject('Movie2_BG')

        for (ChipID, (MovieName, StartPosition, FinishPosition)) in self.param.ChipsParam.iteritems():
            movie = group.getObject(MovieName)
            slot = self.BG.getMovieSlot(ChipID)
            chip = Chip(ChipID, movie, StartPosition, FinishPosition, numbers_of_chips, slot)

            self.Chips[ChipID] = chip

    def set_chips_on_start_position(self):
        with TaskManager.createTaskChain() as tc:
            for chip, parallel in tc.addParallelTaskList(self.Chips.values()):
                parallel.addScope(chip.rotate_to, chip.startPosition)

    # -------------- Main ----------------------------------------------------------------------------------------------
    def set_selected_chip(self, chip):
        self.selected_chip = chip

    def change_chips_position(self, source, chip_1, chip_2):
        with source.addParallelTask(2) as (parallel_1, parallel_2):
            parallel_1.addScope(chip_1.rotate_to, chip_2.currentPosition)

            parallel_2.addScope(chip_2.rotate_to, chip_1.currentPosition)

    def resolve_click_on_chip(self, source, chip):
        with source.addIfTask(bool, chip.isSelected) as (selected, unselected):
            selected.addFunction(chip.set_select, False)
            selected.addFunction(self.set_selected_chip, None)
            selected.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateSegments_Click')

            unselected.addFunction(chip.set_select, True)
            if self.selected_chip is None:
                unselected.addFunction(self.set_selected_chip, chip)
                unselected.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateSegments_Click')
            else:
                with unselected.addParallelTask(2) as (move, sound):
                    move.addScope(self.change_chips_position, chip, self.selected_chip)
                    sound.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateSegments_Move')

                unselected.addFunction(chip.set_select, False)
                unselected.addFunction(self.selected_chip.set_select, False)
                unselected.addFunction(self.set_selected_chip, None)

    def read_holder(self, source, holder):
        click_chip = holder.get()
        source.addScope(self.resolve_click_on_chip, click_chip)

    def click_on_segment(self, source):
        holder_click = Holder()
        for chip, race in source.addRaceTaskList(self.Chips.values()):
            chip.movie.setEnable(True)
            race.addTask('TaskMovie2SocketClick', SocketName='socket', Movie2=chip.movie)
            race.addFunction(holder_click.set, chip)

        source.addScope(self.read_holder, holder_click)

    def complete(self):
        self.enigmaComplete()

    def check_win_combination(self):
        for chip in self.Chips.values():
            if chip.currentPosition != chip.finishPosition:
                return
        self.complete()

    # -------------- Run Task Chain ------------------------------------------------------------------------------------
    def run_task_chain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            tc.addScope(self.click_on_segment)
            tc.addFunction(self.check_win_combination)

    # -------------- Entity --------------------------------------------------------------------------------------------
    def _onPreparation(self):
        super(SwapAndRotateSegments, self)._onPreparation()
        self.load_param()
        self.setup()

    def _onActivate(self):
        super(SwapAndRotateSegments, self)._onActivate()
        self.set_chips_on_start_position()

    def _onDeactivate(self):
        super(SwapAndRotateSegments, self)._onDeactivate()
        self.clean_up()

    # -------------- Enigma control ------------------------------------------------------------------------------------
    def _restoreEnigma(self):
        self._playEnigma()

    def _resetEnigma(self):
        self.clean_up()
        self._playEnigma()

    def _playEnigma(self):
        self.run_task_chain()

    def _skipEnigmaScope(self, source):
        for chip, parallel in source.addParallelTaskList(self.Chips.values()):
            parallel.addNotify(Notificator.onSoundEffectOnObject, self.object, 'SwapAndRotateSegments_Move')
            parallel.addScope(chip.rotate_to, chip.finishPosition)
        source.addFunction(self.check_win_combination)
