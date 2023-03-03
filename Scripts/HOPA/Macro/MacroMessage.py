from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroMessage(MacroCommand):
    def _onValues(self, values):
        self.textID = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if Mengine.existText(self.textID) is False:
                self.initializeFailed("MacroMessage not register textID %s" % (self.textID))
                pass
            pass
        pass

    def _onGenerate(self, source):
        MessageGroup = GroupManager.getGroup("Message")
        WindowFade = DefaultManager.getDefaultFloat("WindowFade", 0.8)

        CurrentSceneName = SceneManager.getCurrentSceneName()

        source.addTask("TaskStateMutex", ID="AliasMessageShow", From=False)
        source.addTask("TaskSceneActivate")
        source.addTask("TaskPrint", Value="MacroMessage %s" % (self.textID,))
        source.addTask("TaskStateChange", ID="AliasMessageShow", Value=True)

        source.addTask("AliasMessageShow", TextID=self.textID)
        if MessageGroup.hasObject("Movie_Open") is True:
            MessageMovie_Open = GroupManager.getObject("Message", "Movie_Open")
            MessageFadeInTime = MessageMovie_Open.getDuration()

            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (tc1, tc2):
                    tc1.addTask("TaskMoviePlay", GroupName="Message", MovieName="Movie_Open", Wait=True)
                    tc2.addTask("AliasFadeIn", FadeGroupName="Fade", To=WindowFade, Time=MessageFadeInTime)
                    pass
                pass
            pass

        Quest = self.addQuest(source, "Message", SceneName=self.SceneName, GroupName=self.GroupName)
        with Quest as tc_quest:
            with tc_quest.addRaceTask(2) as (tc_no, tc_yes):
                tc_no.addTask("AliasMessageNo")
                tc_yes.addTask("AliasMessageYes")
                pass
            pass
        pass

        if MessageGroup.hasObject("Movie_Close") is True:
            MessageMovie_Close = GroupManager.getObject("Message", "Movie_Close")
            MessageFadeOutTime = MessageMovie_Close.getDuration()

            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (tc2, tc3):
                    tc2.addTask("TaskMoviePlay", GroupName="Message", MovieName="Movie_Close", Wait=True)
                    tc3.addTask("AliasFadeOut", FadeGroupName="Fade", Time=MessageFadeOutTime, From=WindowFade)
                    pass
                pass
            pass

        source.addTask("AliasMessageHide", SceneName=CurrentSceneName)
        source.addTask("TaskStateChange", ID="AliasMessageShow", Value=False)

    pass
