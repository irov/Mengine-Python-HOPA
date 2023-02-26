from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.DialogManager import DialogManager

class PolicyDialogAvatar(TaskAlias):
    def _onParams(self, params):
        super(PolicyDialogAvatar, self)._onParams(params)
        self.DialogID = params.get("DialogID")
        self.Dialog = params.get("Dialog")
        pass

    def _onGenerate(self, source):
        DialogPersGroup = DefaultManager.getDefault("DialogPersGroup", None)
        if DialogPersGroup is not None:
            DialogPersGroup = GroupManager.getGroup(DialogPersGroup)
            pass
        else:
            DialogPersGroup = self.Dialog
            pass

        dialogs = DialogManager.getDialogChain(self.DialogID)

        Socket_Next = self.Dialog.getObject("Socket_Next")
        Socket_Next.setParams(Enable=True, Interactive=True, Block=True)
        Text_Message = self.Dialog.getObject("Text_Message")
        Text_Message.setEnable(False)

        Demon_Switch_Avatar = DialogPersGroup.getObject("Demon_Switch_Avatar")
        source.addTask("TaskSetParam", Object=Demon_Switch_Avatar, Param="Switch", Value=dialogs[0].characterID)
        # source.addTask("TaskTransitionBlock", Value = True)

        with source.addParallelTask(2) as (tc, tc1):
            tc.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=0.25, Time=0.2 * 1000, Block=True)  # speed fix

            with tc.addRaceTask(2) as (tc_play, tc_skip):
                for dialog in dialogs:
                    with tc_play.addRaceTask(2) as (tc_play_dialog, tc_play_effect):
                        tc_play_dialog.addTask("AliasDialogSwitchAvatar", Dialog=self.Dialog, CharacterID=dialog.characterID, DialogPersGroup=DialogPersGroup)

                        tc_play_dialog.addTask("TaskDeadLock")

                        with tc_play_effect.addRaceTask(2) as (tc_dialog, tc_next):
                            with tc_dialog.addParallelTask(2) as (tc_voice, tc_text):
                                DialogSound = PolicyManager.getPolicy("DialogSound", "PolicyDummy")
                                if dialog.voiceID is not None and DialogSound == "TaskSoundEffect":
                                    tc_voice.addTask("TaskSoundEffect", SoundName=dialog.voiceID, Wait=True)
                                    pass
                                elif dialog.voiceID is not None:
                                    tc_voice.addTask(DialogSound)
                                    pass
                                else:
                                    tc_voice.addTask("PolicyDummy")
                                    pass

                                DialogTextPlay = PolicyManager.getPolicy("DialogTextPlay", "PolicyDialogStaticText")
                                tc_text.addTask(DialogTextPlay, ObjectText=Text_Message, TextID=dialog.textID)
                                pass

                            tc_dialog.addTask("TaskNotify", ID=Notificator.onDialogMessageComplete, Args=(self.Dialog,))
                            tc_dialog.addTask("TaskDeadLock")

                            DialogShowTime = DefaultManager.getDefaultFloat("DialogShowTime", 0.2)
                            DialogShowTime *= 1000  # speed fix
                            tc_next.addTask("TaskDelay", Time=DialogShowTime)

                            tc_next.addTask("TaskSocketClick", SocketName="Socket_Next")
                            pass
                        pass

                tc_skip.addTask("TaskButtonClick", ButtonName="Button_Skip", AutoEnable=True)
                pass

        source.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=0.25, Time=0.25 * 1000, Unblock=True)  # speed fix
        source.addTask("TaskSetParam", Object=Socket_Next, Param="Interactive", Value=False)
        # source.addTask("TaskTransitionBlock", Value = False)
        pass
    pass