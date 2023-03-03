from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.System import System
from Foundation.TaskManager import TaskManager


class SystemBlockInput(System):
    """
    This class is for handling blocking input from macro, this system should not be global
    """

    # todo: create separate global system guardBlockInputCount and move block input count there

    def __init__(self):
        super(SystemBlockInput, self).__init__()
        self.IsBlocked = False
        self.tc = None

        self.guardBlockCount = 0

    def _onRun(self):
        self.addObserver(Notificator.onBlockInput, self.Block_All_Input)
        self.addObserver(Notificator.onTaskGuardUpdate, self.__cbTaskGuardUpdate)

        return True

    def __cbTaskGuardUpdate(self, bGuard):
        if bGuard:
            self.guardBlockCount += 1
        else:
            self.guardBlockCount -= 1

        # print "guardBlockCount: %d" % self.guardBlockCount

        return False

    def Block_All_Input(self, block):
        if self.Unblock() is True:
            return False
        self.IsBlocked = True

        self.tc = TaskManager.createTaskChain()
        with self.tc as tc:
            with GuardBlockInput(tc) as guard_source:
                guard_source.addBlock()

        return False

    def Unblock(self, block=None, Unblock=None):
        if self.IsBlocked is False:
            return False
        self.IsBlocked = False

        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        return True

    def _onStop(self):
        self.Unblock()

    def _onSave(self):
        return self.IsBlocked

    def _onLoad(self, data_save):
        if data_save is None:
            return

        self.IsBlocked = data_save
