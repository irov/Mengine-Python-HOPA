from Foundation.Task.TaskAlias import TaskAlias

class AliasEnigmaPlay(TaskAlias):

    def _onParams(self, params):
        super(AliasEnigmaPlay, self)._onParams(params)

        self.EnigmaName = params.get("EnigmaName")
        self.EnigmaParams = params.get("EnigmaParams")

    def _onGenerate(self, source):
        with source.addParallelTask(2) as (tc_complete, tc_play):
            tc_complete.addTask("TaskEnigmaComplete", EnigmaName=self.EnigmaName)
            tc_play.addTask("TaskEnigmaPlay", EnigmaName=self.EnigmaName, EnigmaParams=self.EnigmaParams)