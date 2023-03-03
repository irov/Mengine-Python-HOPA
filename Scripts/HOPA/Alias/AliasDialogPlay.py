from Foundation.DefaultManager import DefaultManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.DialogManager import DialogManager


class AliasDialogPlay(TaskAlias):
    def _onParams(self, params):
        super(AliasDialogPlay, self)._onParams(params)
        self.DialogID = params.get("DialogID")
        dialog = DialogManager.getDialog(self.DialogID)
        self.Groups = params.get("Groups", [dialog.group, "Dialog"])
        self.Fade = params.get("Fade", True)
        pass

    def _onGenerate(self, source):
        for group in self.Groups:
            source.addTask("TaskSceneLayerGroupEnable", LayerName=group, Value=True)
            pass

        MusicFadeDialog = DefaultManager.getDefault("MusicFadeDialog", 0.25)

        source.addTask("TaskMusicSetVolume", Tag="Dialog", To=MusicFadeDialog, From=1.0)

        with source.addRaceTask(2) as (tc_play, tc_skip):
            tc_play.addTask("TaskDialogPlay", DialogID=self.DialogID)

            for group in self.Groups:
                tc_play.addTask("TaskSceneLayerGroupEnable", LayerName=group, Value=False)
                pass

            tc_skip.addTask("TaskDialogSkip", DialogID=self.DialogID)
            pass

        # source.addNotify(Notificator.onMusicFadeOut, MusicFadeDialog)
        source.addTask("TaskMusicSetVolume", Tag="Dialog", To=1.0, From=MusicFadeDialog)

