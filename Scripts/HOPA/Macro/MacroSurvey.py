from Foundation.Utils import isSurvey
from HOPA.Macro.MacroCommand import MacroCommand

class MacroSurvey(MacroCommand):

    def _onGenerate(self, source):
        if isSurvey() is False:
            source.addTask("TaskDummy")
            return

        source.addTask("TaskFunction", Fn=self.changeMengineSetting)
        source.addTask("TaskNotify", ID=Notificator.onSurveyComplete)
        source.addTask("AliasTransition", SceneName="SurveyBigFish", Intro=False)
        source.addBlock()

    def changeMengineSetting(self):
        Mengine.changeCurrentAccountSetting("SurveyComplete", u"True")