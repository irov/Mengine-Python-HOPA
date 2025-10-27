from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockMusicVolumeFade import GuardBlockMusicVolumeFade
from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from Functor import Functor
from HOPA.MindManager import MindManager

class Mind(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction("PlayPolicy")
        pass

    def __init__(self):
        super(Mind, self).__init__()
        self.mindId = None
        pass

    def _onRestore(self):
        if self.object.hasObject("Sprite_BlackBar"):
            Sprite_BlackBar = self.object.getObject("Sprite_BlackBar")
            Sprite_BlackBar.setEnable(False)
            pass

        Text_Message = self.object.getObject("Text_Message")
        Text_Message.setEnable(False)
        pass

    def _onDeactivate(self):
        super(Mind, self)._onDeactivate()

        if self.object.hasObject("Sprite_BlackBar"):
            Sprite_BlackBar = self.object.getObject("Sprite_BlackBar")
            Sprite_BlackBar.setEnable(False)
            pass

        Text_Message = self.object.getObject("Text_Message")
        Text_Message.setEnable(False)

        Notification.removeObserver(self.onMindShow)
        Notification.removeObserver(self.onBlackBarRelease)

        if TaskManager.existTaskChain("MindZoomLeave"):
            TaskManager.cancelTaskChain("MindZoomLeave")
            pass

        if TaskManager.existTaskChain("MindPlay"):
            TaskManager.cancelTaskChain("MindPlay")
            pass
        pass

    def _onActivate(self):
        super(Mind, self)._onActivate()

        if self.PlayPolicy is None:
            self.policy = PolicyManager.getPolicy("MindPlay", "PolicyBlackBarPlayStatic")
            pass
        else:
            self.policy = self.PlayPolicy
            pass

        self.onMindShow = Notification.addObserver(Notificator.onMindShow, self.__showBlackBar)
        self.onBlackBarRelease = Notification.addObserver(Notificator.onBlackBarRelease, self.__releaseBlackBar)
        pass

    def __showBlackBar(self, mindId, isZoom, static):
        if self.mindId == mindId:
            return False
        Notification.notify(Notificator.onMindEndlessEnd)
        self.mindId = mindId
        TextID = MindManager.getTextID(mindId)
        DelayTime = MindManager.getDelay(mindId)
        VoiceID = MindManager.getVoiceID(mindId)
        MusicFadeDialog = DefaultManager.getDefault("MusicFadeDialog", 0.25)

        with TaskManager.createTaskChain(Name="MindPlay", Group=self.object,
                                         Cb=Functor(self.__onMindShowComplete, mindId)) as tc:
            with tc.addRaceTask(2) as (tc_mind, tc_voice):
                tc_mind.addTask(self.policy, TextID=TextID, Time=DelayTime, Static=static)
                if VoiceID is None:
                    tc_voice.addBlock()
                else:
                    with GuardBlockMusicVolumeFade(tc_voice, "Dialog", MusicFadeDialog) as tc_Guard:
                        tc_Guard.addTask("TaskVoicePlay", VoiceID=VoiceID, Loop=False, Wait=True)
                        tc_Guard.addBlock()

        if isZoom is False:
            return False
            pass

        with TaskManager.createTaskChain(Name="MindZoomLeave") as tc:
            tc.addTask("TaskZoomLeave", ZoomAny=True)
            tc.addFunction(self.__hideBlackBar)
            pass

        return False
        pass

    def __onMindShowComplete(self, isEnd, mindId):
        self.mindId = None
        Notification.notify(Notificator.onMindPlayComplete, mindId, self.object)

        if TaskManager.existTaskChain("MindZoomLeave"):
            TaskManager.cancelTaskChain("MindZoomLeave")
            pass
        pass

    def __hideBlackBar(self):
        self.mindId = None
        if TaskManager.existTaskChain("MindPlay"):
            TaskManager.cancelTaskChain("MindPlay")
            pass
        pass

    def __releaseBlackBar(self, currentID=None):
        self.__hideBlackBar()

        if TaskManager.existTaskChain("MindZoomLeave"):
            TaskManager.cancelTaskChain("MindZoomLeave")
            pass

        return False
        pass

    pass
