from Foundation.DemonManager import DemonManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Task.TaskAlias import TaskAlias
from Foundation.Utils import getCurrentPublisher

class PolicyNotEnoughGoldDialog(TaskAlias):

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Gold = params.get("Gold")
        self.Descr = params.get("Descr")

        if self.Gold is None and self.Descr is not None:
            if SystemMonetization.hasComponent(self.Descr):
                component = SystemMonetization.getComponent(self.Descr)
                self.Gold = component.getProductPrice()

    def _onGenerate(self, source):
        DialogWindow = DemonManager.getDemon("DialogWindow")
        GameStore = DemonManager.getDemon(SystemMonetization.game_store_name)

        icon = GameStore.generateIcon("Movie2_Coin", "Movie2_Coin_{}".format(getCurrentPublisher()), Enable=True)
        text_args = {"icon_value": [self.Gold]}

        with source.addParallelTask(3) as (window, shopping, cleanup):
            window.addFunction(DialogWindow.runPreset, "NotEnoughMoney", content_style="icon", icon_obj=icon, text_args=text_args)

            with shopping.addRaceTask(2) as (confirm, cancel):
                confirm.addListener(Notificator.onDialogWindowConfirm)
                confirm.addDelay(250)
                confirm.addFunction(GameStore.open, page_id=self.PageID)
                cancel.addListener(Notificator.onDialogWindowCancel)

            with cleanup.addRaceTask(2) as (close, leave):
                close.addEvent(DialogWindow.EVENT_WINDOW_DISAPPEAR)
                leave.addListener(Notificator.onSceneDeactivate)
            cleanup.addTask("TaskObjectDestroy", Object=icon)