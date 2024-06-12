from Foundation.Object.DemonObject import DemonObject
from Foundation.TaskManager import TaskManager

FLOW_TC_NAME = "GiftExchange_Flow"


class ObjectGiftExchange(DemonObject):
    _semaphore_is_open = Semaphore(False, "IsOpen")
    _reset_begin_observer = None
    force_open_trigger_event = Event("ForceOpenTrigger")

    # public

    def runTaskChain(self, button, fade_value, fade_time, fade_group="FadeUI"):
        if TaskManager.existTaskChain(FLOW_TC_NAME) is True:
            Trace.log("Object", 0, "GiftExchange: {!r} already exist".format(FLOW_TC_NAME))
            return

        self.__sceneResetHandler()

        with TaskManager.createTaskChain(Name=FLOW_TC_NAME, Global=True, Repeat=True) as tc:
            with tc.addIfSemaphore(self._semaphore_is_open, True) as (tc_opened, tc_closed):
                with tc_closed.addRaceTask(2) as (tc_click, tc_force):
                    tc_click.addTask("TaskMovie2ButtonClick", Movie2Button=button)
                    tc_force.addEvent(self.force_open_trigger_event)
                tc_closed.addSemaphore(self._semaphore_is_open, To=True)

            with tc.addParallelTask(2) as (tc_fade, tc_layer):
                tc_fade.addTask("AliasFadeIn", FadeGroupName=fade_group, To=fade_value, Time=fade_time)
                tc_layer.addTask("TaskSceneLayerGroupEnable", LayerName="GiftExchange", Value=True)

            with tc.addRepeatTask() as (repeat, until):
                repeat.addScope(self.entity.scopeOpenPlate)
                repeat.addScope(self.entity.scopeRun)

                until.addScope(self.entity.scopeClickQuit)
                until.addScope(self.entity.scopeClosePlate)

            tc.addSemaphore(self._semaphore_is_open, To=False)
            with tc.addParallelTask(2) as (tc_fade, tc_layer):
                tc_fade.addTask("AliasFadeOut", FadeGroupName=fade_group, From=fade_value, Time=fade_time)
                tc_layer.addTask("TaskSceneLayerGroupEnable", LayerName="GiftExchange", Value=False)

    def forceOpenGiftExchange(self):
        """ requires an active task chain (call `runTaskChain` first) """
        if TaskManager.existTaskChain(FLOW_TC_NAME) is False:
            Trace.log("Object", 0, "GiftExchange requires an active flow task chain")
            return
        self.force_open_trigger_event()

    def cancelTaskChain(self):
        if TaskManager.existTaskChain(FLOW_TC_NAME) is True:
            TaskManager.cancelTaskChain(FLOW_TC_NAME)
        if self._reset_begin_observer is not None:
            Notification.removeObserver(self._reset_begin_observer)
            self._reset_begin_observer = None

    def __sceneResetHandler(self):
        def _onSceneRestartBegin():
            if self._semaphore_is_open.getValue() is False:
                return False

            # fixme: FadeIn not working in this case even with delay
            with TaskManager.createTaskChain("GiftExchange_Flow_Reseter") as tc:
                tc.addListener(Notificator.onSceneRestartEnd)
                tc.addFunction(self.force_open_trigger_event)
            return False

        self._reset_begin_observer = Notification.addObserver(Notificator.onSceneRestartBegin, _onSceneRestartBegin)
