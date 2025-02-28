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
        source.addParam(Demon_Switch_Avatar, "Switch", dialogs[0].characterID)

        with source.addParallelTask(2) as (tc, tc_d):
            tc.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=0.25, Time=0.2 * 1000, Block=True)  # speed fix

            for dialog in dialogs:
                tc_d.addParam(Text_Message, "TextID", dialog.textID)
                tc_d.addEnable(Text_Message)
                tc_d.addTask("TaskObjectTextSetMaxVisibleChar", Text=Text_Message)

                # with tc_d.addRaceTask(2) as (tc1, tc2):
                #     tc1.addTask("AliasDialogSwitchAvatar", Dialog = self.Dialog, CharacterID = dialog.characterID, DialogPersGroup = DialogPersGroup, Wait = False)
                #     tc2.addTask("TaskSocketClick", SocketName = "Socket_Next")
                #     pass

                tc_d.addTask("AliasDialogSwitchAvatar", Dialog=self.Dialog, CharacterID=dialog.characterID,
                             DialogPersGroup=DialogPersGroup, Wait=False)

                tc_d.addNotify(Notificator.onDialogMessageComplete, self.Dialog)
                pass

        source.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=0.25, Time=0.25 * 1000, Unblock=True)
        source.addDisable(Text_Message)
        if DialogPersGroupName is not None:
            source.addTask("TaskSceneLayerGroupEnable", LayerName=DialogPersGroupName, Value=False)
