from Foundation.DemonManager import DemonManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Task.TaskAlias import TaskAlias
from Foundation.Utils import getCurrentPublisher
from HOPA.System.SystemEnergy import SystemEnergy


class PolicyNotEnoughEnergyDialog(TaskAlias):

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Action = params.get("Action")

    def _onGenerate(self, source):
        DialogWindow = DemonManager.getDemon("DialogWindow")
        GameStore = DemonManager.getDemon(SystemMonetization.game_store_name)

        icon = GameStore.generateIcon("Movie2_Energy", "Movie2_Energy_{}".format(getCurrentPublisher()), Enable=True)
        text_args = {"icon_value": [SystemEnergy.getActionEnergy(self.Action)]}

        with source.addParallelTask(3) as (window, shopping, cleanup):
            window.addFunction(DialogWindow.runPreset, "NotEnoughEnergy", content_style="icon", icon_obj=icon,
                               text_args=text_args)

            with shopping.addRaceTask(2) as (confirm, cancel):
                confirm.addListener(Notificator.onDialogWindowConfirm)
                confirm.addDelay(250)
                confirm.addFunction(GameStore.open, page_id=self.PageID)
                cancel.addListener(Notificator.onDialogWindowCancel)

            with cleanup.addRaceTask(2) as (close, leave):
                close.addEvent(DialogWindow.EVENT_WINDOW_DISAPPEAR)
                leave.addListener(Notificator.onSceneDeactivate)
            cleanup.addTask("TaskObjectDestroy", Object=icon)
