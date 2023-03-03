from Foundation.DemonManager import DemonManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughEnergyMessage(TaskAlias):

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Action = params.get("Action")

    def _scopeStoreOpen(self, source):
        GameStore = DemonManager.getDemon(SystemMonetization.game_store_name)

        source.addDelay(250)
        source.addFunction(GameStore.open, page_id=self.PageID)

    def _onGenerate(self, source):
        with source.addParallelTask(2) as (tc_fade, tc_message):
            tc_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=250.0)
            tc_message.addTask("AliasSystemMessage", TextID="ID_TEXT_NOT_ENOUGH_ENERGY_MESSAGE",
                               OkID="ID_TEXT_NOT_ENOUGH_ENERGY_CONFIRM", Scope=self._scopeStoreOpen)
        source.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=0.5, Time=250.0)
