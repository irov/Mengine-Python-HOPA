from Foundation.DefaultManager import DefaultManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.DialogManager import DialogManager


class PolicyMonologue(TaskAlias):
    def _onParams(self, params):
        super(PolicyMonologue, self)._onParams(params)
        self.DialogID = params.get("DialogID")
        self.Dialog = params.get("Dialog")
        pass

    def _onGenerate(self, source):
        dialogs = DialogManager.getDialogChain(self.DialogID)

        Socket_Next = self.Dialog.getObject("Socket_Next")
        Socket_Next.setParams(Block=True)
        Text_Message = self.Dialog.getObject("Text_Message")
        Text_Message.setEnable(False)

        # source.addTask("TaskTransitionBlock", Value = True)

        with source.addRaceTask(2) as (tc_play, tc_skip):
            for dialog in dialogs:
                with tc_play.addRaceTask(2) as (tc_dialog, tc_next):
                    with tc_dialog.addParallelTask(2) as (tc_voice, tc_text1):
                        if dialog.voiceID is not None:
                            tc_voice.addTask("TaskSoundEffect", SoundName=dialog.voiceID, Wait=True)
                            pass

                        tc_voice.addDummy()

                        PolicyDialogTextPlay = PolicyManager.getPolicy("DialogTextPlay", "PolicyDialogStaticText")
                        tc_text1.addTask(PolicyDialogTextPlay, ObjectText=Text_Message, TextID=dialog.textID)
                        pass

                    tc_dialog.addNotify(Notificator.onDialogMessageComplete, self.Dialog)
                    #                    tc_dialog.addTask("TaskDeadLock")

                    DialogShowTime = DefaultManager.getDefaultFloat("DialogShowTime", 0.2)
                    DialogShowTime *= 1000  # speed fix
                    tc_next.addDelay(DialogShowTime)
                    #                    tc_next.addTask("TaskMouseButtonClick")
                    tc_next.addTask("TaskSocketClick", SocketName="Socket_Next")

                    tc_next.addTask("TaskObjectTextSetMaxVisibleChar", Text=Text_Message)
                    tc_next.addTask("PolicyDialogStaticText", ObjectText=Text_Message, TextID=dialog.textID)
                    pass
                #                tc_play.addTask("TaskMouseButtonClick")
                tc_play.addTask("TaskSocketClick", SocketName="Socket_Next")
                pass

            tc_skip.addTask("TaskButtonClick", ButtonName="Button_Skip", AutoEnable=True)

        # source.addTask("TaskTransitionBlock", Value = False)
        pass

    pass
