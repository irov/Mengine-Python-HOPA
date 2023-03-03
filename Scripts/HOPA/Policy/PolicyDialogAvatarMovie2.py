from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.DialogManager import DialogManager


class PolicyDialogAvatarMovie2(TaskAlias):
    def _onParams(self, params):
        super(PolicyDialogAvatarMovie2, self)._onParams(params)
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
        Text_Message = self.Dialog.getObject("Text_Message")
        Text_Message.setEnable(False)

        Demon_Switch_Avatar = DialogPersGroup.getObject("Demon_Switch_Avatar")
        source.addTask("TaskSetParam", Object=Demon_Switch_Avatar, Param="Switch", Value=dialogs[0].characterID)

        with source.addParallelTask(2) as (tc, tc_d):
            tc.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=0.25, Time=0.2 * 1000, Block=True)  # speed fix

            for dialog in dialogs:
                tc_d.addTask("TaskSetParam", Object=Text_Message, Param="TextID", Value=dialog.textID)
                tc_d.addTask("TaskEnable", Object=Text_Message, Value=True)
                tc_d.addTask("TaskObjectTextSetMaxVisibleChar", Text=Text_Message)

                # with tc_d.addRaceTask(2) as (tc1, tc2):
                #     tc1.addTask("AliasDialogSwitchAvatar", Dialog = self.Dialog, CharacterID = dialog.characterID, DialogPersGroup = DialogPersGroup, Wait = False)
                #     tc2.addTask("TaskSocketClick", SocketName = "Socket_Next")
                #     pass

                tc_d.addTask("AliasDialogSwitchAvatar", Dialog=self.Dialog, CharacterID=dialog.characterID,
                             DialogPersGroup=DialogPersGroup, Wait=False)

                tc_d.addTask("TaskNotify", ID=Notificator.onDialogMessageComplete, Args=(self.Dialog,))
                pass

        source.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=0.25, Time=0.25 * 1000, Unblock=True)
        source.addTask("TaskEnable", Object=Text_Message, Value=False)
        if DialogPersGroupName is not None:
            source.addTask("TaskSceneLayerGroupEnable", LayerName=DialogPersGroupName, Value=False)
