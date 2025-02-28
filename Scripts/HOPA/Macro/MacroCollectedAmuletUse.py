from Foundation.DemonManager import DemonManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroCollectedAmuletUse(MacroCommand):
    def _onGenerate(self, source):
        Demon = DemonManager.getDemon("CollectedAmulet")
        Socket = Demon.getObject("Socket_Amulet")
        Quest = self.addQuest(source, "Click", SceneName=self.SceneName, GroupName=self.GroupName, Object=Socket)

        def setValid():
            DemonEntity = Demon.getEntity()
            DemonEntity.setValid(True)
            pass

        with Quest as tc_quest:
            tc_quest.addFunction(setValid)
            tc_quest.addListener(Notificator.onCollectedAmuletUse)
