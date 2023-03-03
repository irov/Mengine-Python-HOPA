from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockMusicVolumeFade import GuardBlockMusicVolumeFade
from Foundation.TaskManager import TaskManager
from HOPA.DialogBoxManager import DialogBoxManager


class DialogBox(BaseEntity):
    def _onPreparation(self):
        super(DialogBox, self)._onPreparation()
        if self.object.hasObject("Sprite_AvatarFrame"):
            Sprite_AvatarFrame = self.object.getObject("Sprite_AvatarFrame")
            Sprite_AvatarFrame.setEnable(False)

        if self.object.hasObject("Sprite_AvatarBG"):
            Sprite_AvatarBG = self.object.getObject("Sprite_AvatarBG")
            Sprite_AvatarBG.setEnable(False)

        if self.object.hasObject("Sprite_BlackBar"):
            Sprite_BlackBar = self.object.getObject("Sprite_BlackBar")
            Sprite_BlackBar.setEnable(False)

        Text_Message = self.object.getObject("Text_Message")
        Text_Message.setEnable(False)

    def _onActivate(self):
        super(DialogBox, self)._onActivate()

        self.onDialogBoxShow = Notification.addObserver(Notificator.onDialogBoxShow, self.__showDialogBox)
        self.onDialogBoxRelease = Notification.addObserver(Notificator.onDialogBoxShowRelease, self.__releaseDialogBox)
        # self.onZoomLeave= Notification.addObserver(Notificator.onZoomLeave, self.__releaseDialogBox)

    def _onDeactivate(self):
        super(DialogBox, self)._onDeactivate()

        if self.object.hasObject("Sprite_AvatarFrame"):
            Sprite_AvatarFrame = self.object.getObject("Sprite_AvatarFrame")
            Sprite_AvatarFrame.setEnable(False)

        if self.object.hasObject("Sprite_AvatarBG"):
            Sprite_AvatarBG = self.object.getObject("Sprite_AvatarBG")
            Sprite_AvatarBG.setEnable(False)

        if self.object.hasObject("Sprite_BlackBar"):
            Sprite_BlackBar = self.object.getObject("Sprite_BlackBar")
            Sprite_BlackBar.setEnable(False)

        Text_Message = self.object.getObject("Text_Message")
        Text_Message.setEnable(False)

        Notification.removeObserver(self.onDialogBoxShow)
        Notification.removeObserver(self.onDialogBoxRelease)

        if TaskManager.existTaskChain("DialogBoxPlay"):
            TaskManager.cancelTaskChain("DialogBoxPlay")
            pass

    def __showDialogBox(self, dialogIDs):
        MusicFadeDialog = DefaultManager.getDefault("MusicFadeDialog", 0.25)

        with TaskManager.createTaskChain(Name="DialogBoxPlay", Group=self.object,
                                         Cb=Functor(self.__onDialogBoxPlayComplete, dialogIDs)) as tc:
            with GuardBlockMusicVolumeFade(tc, "Dialog", MusicFadeDialog) as source:
                for dialogID in dialogIDs:
                    source.addScope(self.__scopeDialogBoxPlay, dialogID)

        return False
        pass

    def __scopeDialogBoxPlay(self, source, dialogID):
        dialog = DialogBoxManager.getDialog(dialogID)

        TextID = dialog.textID
        CharacterID = dialog.characterID
        VoiceID = dialog.voiceID

        if dialog is not None:
            AlphaToTime = dialog.AlphaToTime
            AlphaFromTime = dialog.AlphaFromTime
            PlayDialogDelay = dialog.PlayDialogDelay
        else:
            AlphaToTime = 1000
            AlphaFromTime = 500
            PlayDialogDelay = 100

        source.addTask("TaskTextSetTextID", TextName="Text_Message", Value=TextID)

        with source.addParallelTask(5) as (tc_avatar_frame, tc_avatar_bg, tc_black_bar, tc_avatar, tc_text):
            if self.object.hasObject("Sprite_AvatarFrame"):
                tc_avatar_frame.addTask("TaskEnable", ObjectName="Sprite_AvatarFrame")
                tc_avatar_frame.addTask("AliasObjectAlphaTo", ObjectName="Sprite_AvatarFrame",
                                        Time=AlphaToTime, From=0.0, To=1.0)

            if self.object.hasObject("Sprite_AvatarBG"):
                tc_avatar_bg.addTask("TaskEnable", ObjectName="Sprite_AvatarBG")
                tc_avatar_bg.addTask("AliasObjectAlphaTo", ObjectName="Sprite_AvatarBG",
                                     Time=AlphaToTime, From=0.0, To=1.0)

            if self.object.hasObject("Sprite_BlackBar"):
                tc_black_bar.addTask("TaskEnable", ObjectName="Sprite_BlackBar")
                tc_black_bar.addTask("AliasObjectAlphaTo", ObjectName="Sprite_BlackBar",
                                     Time=AlphaToTime, From=0.0, To=1.0)

            if self.object.hasObject(CharacterID):
                tc_avatar.addTask("TaskEnable", ObjectName=CharacterID)
                tc_avatar.addTask("AliasObjectAlphaTo", ObjectName=CharacterID, Time=AlphaToTime, From=0.0, To=1.0)

            if self.object.hasObject("Text_Message"):
                tc_text.addTask("TaskEnable", ObjectName="Text_Message")
                tc_text.addTask("AliasObjectAlphaTo", ObjectName="Text_Message", Time=AlphaToTime, From=0.0, To=1.0)
        source.addTask("TaskDelay", Time=PlayDialogDelay)

        with source.addRaceTask(2) as (voice_play_tc, skip_voice_play_tc):
            voice_play_tc.addTask("TaskVoicePlay", VoiceID=VoiceID, Loop=False, Wait=True)

            skip_voice_play_tc.addListener(Notificator.onAppendFoundItemsHOG2)

        # TextDelay = 0.05  # sec
        # with source.addParallelTask(2) as (tc_voice, tc_text):
        #     tc_voice.addTask("TaskSoundEffect", SoundName=VoiceID)
        #
        #     ObjectText = self.object.getObject("Text_Message")
        #
        #     tc_text.addTask("AliasTextPlay", ObjectText=ObjectText, TextID=TextID, TextDelay=TextDelay)

        source.addTask("TaskDelay", Time=PlayDialogDelay)

        with source.addParallelTask(5) as (tc_avatar_frame, tc_avatar_bg, tc_black_bar, tc_avatar, tc_text):
            if self.object.hasObject("Sprite_AvatarFrame"):
                tc_avatar_frame.addTask("AliasObjectAlphaTo", ObjectName="Sprite_AvatarFrame", Time=AlphaFromTime, To=0.0)
                tc_avatar_frame.addTask("TaskEnable", ObjectName="Sprite_AvatarFrame", Value=False)

            if self.object.hasObject("Sprite_AvatarBG"):
                tc_avatar_bg.addTask("AliasObjectAlphaTo", ObjectName="Sprite_AvatarBG", Time=AlphaFromTime, To=0.0)
                tc_avatar_bg.addTask("TaskEnable", ObjectName="Sprite_AvatarBG", Value=False)

            if self.object.hasObject("Sprite_BlackBar"):
                tc_black_bar.addTask("AliasObjectAlphaTo", ObjectName="Sprite_BlackBar", Time=AlphaFromTime, To=0.0)
                tc_black_bar.addTask("TaskEnable", ObjectName="Sprite_BlackBar", Value=False)

            if self.object.hasObject(CharacterID):
                tc_avatar.addTask("AliasObjectAlphaTo", ObjectName=CharacterID, Time=AlphaFromTime, To=0.0)
                tc_avatar.addTask("TaskEnable", ObjectName=CharacterID, Value=False)

            if self.object.hasObject("Text_Message"):
                tc_text.addTask("AliasObjectAlphaTo", ObjectName="Text_Message", Time=AlphaFromTime, To=0.0)
                tc_text.addTask("TaskEnable", ObjectName="Text_Message", Value=False)

        pass

    def __onDialogBoxPlayComplete(self, isEnd, dialogIDs):
        dialogID = dialogIDs[-1]
        dialog = DialogBoxManager.getDialog(dialogID)

        CharacterID = dialog.characterID
        if self.object.hasObject(CharacterID):
            Sprite_Character = self.object.getObject(CharacterID)
            Sprite_Character.setEnable(False)

        Notification.notify(Notificator.onDialogBoxPlayComplete, dialogID)
        pass

    def __releaseDialogBox(self, dialogID=None):
        if TaskManager.existTaskChain("DialogBoxPlay"):
            TaskManager.cancelTaskChain("DialogBoxPlay")
            pass

        return False
