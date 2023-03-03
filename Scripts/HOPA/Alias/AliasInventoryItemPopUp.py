from Foundation.GuardBlockGame import GuardBlockGame
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryItemPopUp(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryItemPopUp, self)._onParams(params)

        self.ItemName = params.get("ItemName")
        self.Inventory = params.get("Inventory")

    def _onGenerate(self, source):
        with GuardBlockGame(source) as source:
            source.addTask("TaskSceneActivate")

            source.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=0.3, Time=0.2 * 1000.0, Block=True)

            source.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=True)

            source.addTask("TaskItemPopUp", GroupName="ItemPopUp", ItemName=self.ItemName)

            source.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=False)

            source.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=False)
