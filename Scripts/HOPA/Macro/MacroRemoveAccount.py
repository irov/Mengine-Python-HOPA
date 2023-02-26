from HOPA.Macro.MacroCommand import MacroCommand

class MacroRemoveAccount(MacroCommand):
    def _onValues(self, values):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskFunction", Fn=self.changeMengineSetting)
        source.addTask("TaskNotify", ID=Notificator.onRemoveAccount)
        pass

    def changeMengineSetting(self):
        Mengine.changeCurrentAccountSettingBool("GameComplete", True)
        pass
    pass