from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager

class PuzzleButtons(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "Slot")
        pass

    def __init__(self):
        super(PuzzleButtons, self).__init__()
        self.ParentLayer = "Puzzle"
        self.ButtonReset = None
        self.reloadBlock = None
        self.Layer = None
        self.InstructionGroupName = None
        self.Movie_Reload = None
        self.ButtonInstruction = None
        self.InstructionGroupName = None
        pass

    def _onActivate(self):
        self.reloadBlock = True

        self.preparation()
        self.onButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)

        LoadSkipTime = Mengine.getCurrentAccountSettingFloat("DifficultyCustomSkipTime")
        # HintMaxRelodTime = DefaultManager.getDefaultFloat("HintMaxRelodTime", 500)
        # LoadSkipTime = SkipTimeCoef * HintMaxRelodTime
        #
        # LoadSkipTime *= 1000  # speed fix

        if self.Movie_Reload is not None:
            Movie_ReloadDuration = self.Movie_Reload.getDuration()

            if Movie_ReloadDuration != LoadSkipTime:
                speedFactor = Movie_ReloadDuration / LoadSkipTime

                self.Movie_Reload.setSpeedFactor(speedFactor)
                pass

            self.Movie_Reload.setLastFrame(False)

            with TaskManager.createTaskChain(Name="ReloadSkip") as tc_skip:
                tc_skip.addTask("TaskMoviePlay", Movie=self.Movie_Reload)
                tc_skip.addFunction(self.turnOffReload)
                pass
            pass
        else:
            self.turnOffReload()
            pass

        if self.ButtonInstruction is not None and self.InstructionGroupName is not None and self.ButtonOk is not None:
            with TaskManager.createTaskChain(Name="PuzzleButtons_Instruction", Repeat=True) as tc_inst:
                tc_inst.addTask("TaskButtonClick", Button=self.ButtonInstruction)
                tc_inst.addTask("TaskSceneLayerGroupEnable", LayerName=self.InstructionGroupName, Value=True)
                tc_inst.addFunction(self.blockInput)
                tc_inst.addTask("TaskButtonClick", Button=self.ButtonOk)
                tc_inst.addTask("TaskSceneLayerGroupEnable", LayerName=self.InstructionGroupName, Value=False)
                pass
            pass

        pass

    def blockInput(self):
        BlockSocket = self.Instruction.getObject("Socket_Block")
        BlockSocket.setInteractive(True)
        BlockSocket.setBlock(True)
        pass

    def turnOffReload(self):
        self.reloadBlock = False
        pass

    def _onDeactivate(self):
        Notification.removeObserver(self.onButtonClickObserver)

        if TaskManager.existTaskChain("ReloadSkip"):
            TaskManager.cancelTaskChain("ReloadSkip")
            pass

        if TaskManager.existTaskChain("PuzzleButtons_Instruction"):
            TaskManager.cancelTaskChain("PuzzleButtons_Instruction")
            pass
        pass

    def __onButtonClick(self, button):
        if ArrowManager.emptyArrowAttach() is False:
            return False
            pass
        if button is self.ButtonReset:
            Notification.notify(Notificator.onEnigmaReset)
            return False
            pass
        elif button is self.ButtonSkip:
            if self.reloadBlock is True:
                return False
            Notification.notify(Notificator.onEnigmaSkip)
            self.turns_buttons(False, skip=True)
            self.reloadBlock = True

            if TaskManager.existTaskChain("PuzzleButtons_Instruction"):
                TaskManager.cancelTaskChain("PuzzleButtons_Instruction")
                pass
            return False
            pass

        return False
        pass

    def preparation(self):
        self.ButtonReset = None
        if self.object.hasObject("Button_Reset"):
            self.ButtonReset = self.object.getObject('Button_Reset')
            self.ButtonReset.setInteractive(True)
            pass

        self.ButtonSkip = None
        if self.object.hasObject("Button_Skip"):
            self.ButtonSkip = self.object.getObject('Button_Skip')
            self.ButtonSkip.setInteractive(True)
            pass

        if self.object.hasObject("Movie_Reload"):
            self.Movie_Reload = self.object.getObject("Movie_Reload")
            self.setSkipReload()
            pass

        self.ButtonInstruction = None
        if self.object.hasObject("Button_Instruction"):
            self.ButtonInstruction = self.object.getObject('Button_Instruction')

            self.Instruction = self.getInstructionGroup()
            if self.Instruction is None:
                return False
                pass

            self.ButtonOk = None
            if self.Instruction.hasObject("Button_OK") is True:
                self.ButtonOk = self.Instruction.getObject("Button_OK")
                pass
            pass

        pass

    def getInstructionGroup(self):
        if self.Slot is not None:
            self.InstructionGroupName = self.Slot
            Group = GroupManager.getGroup(self.InstructionGroupName)
            return Group
            pass

        self.InstructionGroupName = "PuzzleInstruction"

        SceneName = SceneManager.getCurrentSceneName()
        Slot = SceneManager.getSceneDescription(SceneName)
        groupName = Slot.getSlotsGroup(self.InstructionGroupName)

        if groupName is None:
            Trace.log("Entity", 0, "PuzzleButtons Instruction is None, not add to DefaultSlots_[current].xlsx")
            return None
            pass

        Group = GroupManager.getGroup(groupName)
        return Group
        pass

    def setSkipReload(self):
        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        TypeTime = "SpinCircleReload%s" % (Difficulty)
        self.SkipTime = DefaultManager.getDefaultFloat(TypeTime, 5)
        self.SkipTime *= 1000  # speed fix

        if self.Movie_Reload is not None:
            Duration = self.Movie_Reload.getDuration()
            speedFactor = Duration / self.SkipTime
            self.Movie_Reload.setSpeedFactor(speedFactor)
            pass
        pass

    def turns_buttons(self, value, skip=False):
        if self.ButtonReset is not None:
            self.ButtonReset.setInteractive(value)
            pass

        if self.ButtonSkip is not None:
            self.ButtonSkip.setInteractive(value)
            pass
        pass

    pass
