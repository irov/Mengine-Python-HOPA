from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasPetItem(TaskAlias):
    def _onParams(self, params):
        super(AliasPetItem, self)._onParams(params)
        self.Socket = params.get("Socket")
        self.ItemName = params.get("ItemName")
        self.SceneName = params.get("SceneName")
        self.GroupName = params.get("Group_Name")
        self.MovieName = params.get("MovieName")

    def _onGenerate(self, source):
        movie = GroupManager.getObject(self.GroupName, self.MovieName)
        source.addTask("TaskNotify", ID=Notificator.onPetPush, Args=(self.Socket, self.ItemName, self.GroupName, movie))
        source.addTask("TaskListener", ID=Notificator.onPetComplete, Filter=self.__filter)

    def __filter(self, itemName, sceneName):
        if itemName == self.ItemName:
            return True
        return False
