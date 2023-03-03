from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.SemaphoreManager import SemaphoreManager


class FreezeHOG(BaseEntity):
    def __init__(self):
        super(FreezeHOG, self).__init__()
        self.tc = None
        self.semaphore = SemaphoreManager.getSemaphore("SkipFreezeHOGCounter")
        self.fail_number = DefaultManager.getDefaultInt("NumberOfFailClickForFreezeHOG", 5)

    def _onActivate(self):
        self.__runTaskChain()

    def __runTaskChain(self):
        current_scene_name = SceneManager.getCurrentSceneName()
        if not GroupManager.hasObject(current_scene_name, "Socket_SocketFreeze"):
            return False

        self.movie_freeze = self.object.getObject("Movie2_Freeze")

        self.tc = TaskManager.createTaskChain(Name="FreezeHOG", Repeat=True)
        with self.tc as tc:
            with tc.addRaceTask(2) as (fail_tc, skip_counter_tc):
                for i in range(self.fail_number):
                    fail_tc.addTask("TaskSocketClick", SocketName="Socket_SocketFreeze", GroupName=current_scene_name)

                with GuardBlockInput(fail_tc) as guard_fail_tc:
                    guard_fail_tc.addEnable(self.movie_freeze)
                    guard_fail_tc.addPlay(self.movie_freeze, Wait=True)
                    guard_fail_tc.addDisable(self.movie_freeze)

                skip_counter_tc.addSemaphore(self.semaphore, From=True, To=False)

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None
