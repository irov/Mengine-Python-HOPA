from Foundation.Task.TaskAlias import TaskAlias

class AliasObjective(TaskAlias):
    def _onParams(self, params):
        super(AliasObjective, self)._onParams(params)

        self.ObjectiveID = params.get("ObjectiveID")
        pass

    def _onGenerate(self, source):
        #        source.addTask("TaskSoundEffect", SoundName = "ObjectiveAppearance", Wait = False)
        source.addTask("TaskObjective", ObjectiveID=self.ObjectiveID)
        #        source.addTask("TaskPrint", Value = "Objective %s"%(self.ObjectiveID))
        pass
    pass