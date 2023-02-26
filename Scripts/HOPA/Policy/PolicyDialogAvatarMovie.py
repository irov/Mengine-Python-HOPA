from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.DialogManager import DialogManager

class PolicyDialogAvatarMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyDialogAvatarMovie, self)._onParams(params)
        self.DialogID = params.get("DialogID")
        self.Dialog = params.get("Dialog")
        pass

    def _onGenerate(self, source):
        DialogPersGroupName = DefaultManager.getDefault("DialogPersGroup", None)
        if DialogPersGroupName is not None:
            DialogPersGroup = GroupManager.getGroup(DialogPersGroupName)
            source.addTask("TaskSceneLayerGroupEnable", LayerName=DialogPersGroupName, Value=True)
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

            with tc1.addRaceTask(2) as (tc_play, tc_skip):
                for dialog in dialogs:
                    with tc_play.addRaceTask(2) as (tc_dialog, tc_next):
                        with tc_dialog.addParallelTask(3) as (tc_dialog1, tc_dialog2, tc_dialog3):
                            tc_dialog1.addTask("AliasDialogSwitchAvatar", Dialog=self.Dialog, CharacterID=dialog.characterID, DialogPersGroup=DialogPersGroup, Wait=False)

                            DialogTextPlay = PolicyManager.getPolicy("DialogTextPlay", "PolicyDialogStaticText")
                            tc_dialog2.addTask(DialogTextPlay, ObjectText=Text_Message, TextID=dialog.textID)

                            DialogSound = PolicyManager.getPolicy("DialogSound", "PolicyDummy")
                            if dialog.voiceID is not None and DialogSound == "TaskSoundEffect":
                                tc_dialog3.addTask("TaskSoundEffect", SoundName=dialog.voiceID, Wait=True)
                                pass
                            elif dialog.voiceID is not None:
                                tc_dialog3.addTask(DialogSound)
                                pass
                            else:
                                tc_dialog3.addTask("TaskDummy")
                                pass
                            pass

                        DialogShowTime = DefaultManager.getDefaultFloat("DialogShowTime", 0.2)
                        DialogShowTime *= 1000  # speed fix
                        tc_next.addTask("TaskDelay", Time=DialogShowTime)
                        tc_next.addTask("TaskSocketClick", SocketName="Socket_Next")
                        # tc_next.addTask("TaskFunction", Fn = self.__cancelText)
                        tc_next.addTask("TaskObjectTextSetMaxVisibleChar", Text=Text_Message)
                        tc_next.addTask("PolicyDialogStaticText", ObjectText=Text_Message, TextID=dialog.textID)
                        pass

                tc_play.addTask("TaskNotify", ID=Notificator.onDialogMessageComplete, Args=(self.Dialog,))
                tc_play.addTask("TaskSocketClick", SocketName="Socket_Next")

                tc_skip.addTask("TaskButtonClick", ButtonName="Button_Skip", AutoEnable=True)
                pass

        source.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=0.25, Time=0.25 * 1000, Unblock=True)  # speed fix
        source.addTask("TaskSetParam", Object=Socket_Next, Param="Interactive", Value=False)
        source.addTask("TaskEnable", Object=Text_Message, Value=False)
        if DialogPersGroupName is not None:
            source.addTask("TaskSceneLayerGroupEnable", LayerName=DialogPersGroupName, Value=False)
            pass
        # source.addTask("TaskTransitionBlock", Value = False)
        pass
    pass