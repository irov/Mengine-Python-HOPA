from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockGame import GuardBlockGame
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.DialogManager import DialogManager

class PolicyDialogVoiceAvatar(TaskAlias):
    def _onParams(self, params):
        super(PolicyDialogVoiceAvatar, self)._onParams(params)
        self.DialogID = params.get("DialogID")
        self.Dialog = params.get("Dialog")
        self.Fade = params.get("Fade")
        pass

    def _onGenerate(self, source):
        dialogs = DialogManager.getDialogChain(self.DialogID)

        DialogShowTime = DefaultManager.getDefaultFloat("DialogShowTime", 0.2)
        DialogShowTime *= 1000  # speed fix

        DialogFadeTo = DefaultManager.getDefaultFloat("DialogFadeAlpha", 0.25)
        DialogFadeTime = DefaultManager.getDefaultFloat("DialogFadeTime", 0.2)
        DialogFadeTime *= 1000  # speed fix

        Text_Message = self.Dialog.getObject("Text_Message")
        Text_Message.setEnable(False)

        Demon_Switch_Avatar = self.Dialog.getObject("Demon_Switch_Avatar")
        DialogTextPlay = PolicyManager.getPolicy("DialogTextPlay", "PolicyDialogStaticText")
        DialogSound = PolicyManager.getPolicy("DialogSound", "PolicyDummy")

        source.addTask("TaskSetParam", Object=Demon_Switch_Avatar, Param="Switch", Value=dialogs[0].characterID)

        with GuardBlockGame(source) as tc:
            with tc.addParallelTask(3) as (tc_Fade, tc1, tc_SceneEffect):
                tc_Fade.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=DialogFadeTo, Time=DialogFadeTime, FromIdle=True, ResetFadeCount=True)

                if GroupManager.hasObject("Dialog", "Movie2_Open") is True:
                    tc_SceneEffect.addTask("TaskMovie2Play", GroupName="Dialog", Movie2Name="Movie2_Open", Wait=True)

                with tc1.addRaceTask(3) as (tc_play, tc_skip_button, tc_skip_socket):
                    for dialog in dialogs:
                        with tc_play.addRaceTask(2) as (tc_dialog, tc_next):
                            with tc_dialog.addParallelTask(3) as (tc_voice, tc_text, tc_play_dialog):
                                if dialog.voiceID is not None and DialogSound == "TaskSoundEffect":
                                    tc_voice.addTask("TaskVoicePlay", VoiceID=dialog.voiceID, Wait=True)
                                    pass
                                elif dialog.voiceID is not None:
                                    tc_voice.addTask(DialogSound)
                                    pass
                                else:
                                    tc_voice.addTask("PolicyDummy")
                                    pass

                                tc_text.addTask(DialogTextPlay, ObjectText=Text_Message, TextID=dialog.textID, TextDelay=dialog.textDelay, AudioDuration=dialog.audio_duration)

                                tc_play_dialog.addTask("AliasDialogSwitchAvatar", Dialog=self.Dialog, DialogPersGroup=self.Dialog, CharacterID=dialog.characterID, IdleID=dialog.idleID, Wait=False)

                            tc_dialog.addNotify(Notificator.onDialogMessageComplete, self.Dialog)
                            if dialog.finish is not True:
                                tc_dialog.addTask("TaskDeadLock")
                            else:
                                tc_dialog.addDelay(1000.0)

                            tc_next.addTask("TaskDelay", Time=DialogShowTime)
                            tc_next.addTask("TaskMovie2ButtonClick", GroupName="Dialog", Movie2ButtonName="Movie2Button_Next", AutoEnable=True)

                            pass

                    tc_skip_button.addTask("TaskMovie2ButtonClick", GroupName="Dialog", Movie2ButtonName="Movie2Button_Skip", AutoEnable=True)
                    tc_skip_socket.addBlock()

            tc.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=DialogFadeTo, Time=DialogFadeTime, Block=False)

            tc.addParam(Demon_Switch_Avatar, "Switch", None)
            tc.addTask("TaskEnable", Object=Text_Message, Value=False)