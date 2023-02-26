from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.QuestManager import QuestManager

class AliasObjectClick(MixinObject, TaskAlias):
    def _onParams(self, params):
        super(AliasObjectClick, self)._onParams(params)
        self.SceneName = params.get("SceneName", None)
        self.AutoEnable = params.get("AutoEnable", True)
        self.IsQuest = params.get("IsQuest", False)
        pass

    def _onGenerate(self, source):
        ObjectType = self.Object.getType()
        if self.IsQuest is True:
            Quest = QuestManager.createLocalQuest("Click", SceneName=self.SceneName, GroupName=self.GroupName, Object=self.Object)
            with QuestManager.runQuest(source, Quest) as tc_quest:
                if ObjectType == "ObjectInteraction":
                    tc_quest.addTask("TaskInteraction", Interaction=self.Object)

                elif ObjectType == "ObjectSocket":
                    tc_quest.addTask("TaskSocketClick", Socket=self.Object, AutoEnable=self.AutoEnable)

                elif ObjectType == "ObjectTransition":
                    tc_quest.addTask("TaskTransitionClick", Transition=self.Object)

                elif ObjectType == "ObjectZoom":
                    tc_quest.addTask("TaskZoomClick", Zoom=self.Object)

                elif ObjectType == "ObjectItem":
                    tc_quest.addTask("TaskItemClick", Item=self.Object)

                elif ObjectType == "ObjectFan":
                    tc_quest.addTask("TaskFanClick", Fan=self.Object)

                elif ObjectType == "ObjectButton":
                    tc_quest.addTask("TaskButtonClick", Button=self.Object)

                elif ObjectType == "ObjectMovieButton":
                    source.addTask("TaskMovieButtonClick", MovieButton=self.Object)

                elif ObjectType == "ObjectMovie2Button":
                    source.addTask("TaskMovie2ButtonClick", Movie2Button=self.Object)

                elif ObjectType == "ObjectMovieItem":
                    source.addTask("TaskMovieItemClick", MovieItem=self.Object)

                elif ObjectType == "ObjectMovie2Item":
                    source.addTask("TaskMovieItemClick", MovieItem=self.Object)

                elif ObjectType == "ObjectMovie2":
                    # macro race case fix
                    if not self.AutoEnable and not self.Object.getEnable():
                        source.addBlock()
                        return

                    source.addTask("TaskMovie2SocketClick", Movie2=self.Object, Any=True)
            return

        if ObjectType == "ObjectInteraction":
            source.addTask("TaskInteraction", Interaction=self.Object)

        elif ObjectType == "ObjectSocket":
            source.addTask("TaskSocketClick", Socket=self.Object, AutoEnable=self.AutoEnable)

        elif ObjectType == "ObjectTransition":
            source.addTask("TaskTransitionClick", Transition=self.Object)

        elif ObjectType == "ObjectZoom":
            source.addTask("TaskZoomClick", Zoom=self.Object)

        elif ObjectType == "ObjectItem":
            source.addTask("TaskItemClick", Item=self.Object)

        elif ObjectType == "ObjectFan":
            source.addTask("TaskFanClick", Fan=self.Object)

        elif ObjectType == "ObjectButton":
            source.addTask("TaskButtonClick", Button=self.Object)

        elif ObjectType == "ObjectMovieButton":
            source.addTask("TaskMovieButtonClick", MovieButton=self.Object)

        elif ObjectType == "ObjectMovieItem":
            source.addTask("TaskMovieItemClick", MovieItem=self.Object)

        elif ObjectType == "ObjectMovie2Item":
            source.addTask("TaskMovieItemClick", MovieItem=self.Object)

        elif ObjectType == "ObjectMovie2":
            if not self.AutoEnable and not self.Object.getEnable():
                source.addBlock()
                return

            source.addTask("TaskMovie2SocketClick", Movie2=self.Object, Any=True)