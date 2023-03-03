from Foundation.Task.TaskAlias import TaskAlias


class AliasBoneUsage(TaskAlias):
    def _onParams(self, params):
        super(AliasBoneUsage, self)._onParams(params)
        self.bone_repr = params.get("Bone")
        self.SceneName = params.get("SceneName")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onBoneUse, Args=(self.bone_repr, self.SceneName))
        source.addTask("TaskListener", ID=Notificator.onBoneUse, Filter=self.on_used)
        pass

    pass

    def on_used(self, repr, group=None):
        if repr == "done:%s" % (self.bone_repr,):
            return True
            pass
        return False
        pass

    pass
