"""
Created on 13.09.2011

@author: Me
"""

from Foundation.Task.MixinObjectTemplate import MixinFan
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.FanItemManager import FanItemManager
from HOPA.FanManager import FanManager
from HOPA.QuestManager import QuestManager

class AliasFanFindItem(MixinFan, TaskAlias):
    def _onParams(self, params):
        super(AliasFanFindItem, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        self.SceneName = params.get("SceneName")
        pass

    def _onGenerate(self, source):
        ItemObject = FanItemManager.getItemObject(self.ItemName)
        ItemEntity = ItemObject.getEntity()
        Pos = ItemObject.getPosition()
        ItemObjectName = ItemObject.getName()
        ItemObjectGroup = ItemObject.getGroup()

        with source.addRepeatTask() as (tc_do, tc_until):
            tc_do.addTask("TaskItemClick", Item=ItemObject)
            tc_do.addTask("TaskFunction", Fn=FanManager.openFan, Args=(self.Fan,))

            tc_do.addTask("TaskArrowAttach", Object=ItemObject)
            tc_do.addTask("TaskFanItemInHand", FanItem=ItemObject)

            tc_do.addTask("TaskItemInvalidUse", Item=ItemObject)

            tc_do.addTask("TaskFanItemInNone", FanItem=ItemObject)
            tc_do.addTask("TaskRemoveArrowAttach")
            tc_do.addTask("TaskNodeRemoveFromParent", Node=ItemEntity)

            tc_do.addTask("TaskObjectReturn", Object=ItemObject)
            tc_do.addTask("TaskObjectSetPosition", Object=ItemObject, Value=Pos)

            Quest = QuestManager.createLocalQuest("Fan", SceneName=self.SceneName, GroupName=ItemObjectGroup, ItemObjectName=ItemObjectName)
            with QuestManager.runQuest(tc_until, Quest) as tc_quest:
                tc_quest.addTask("TaskFanUse", GroupName=self.GroupName, FanName=self.FanName, Item=ItemObject)
                pass
            pass

        source.addTask("TaskFanFoundItem", GroupName=self.GroupName, FanName=self.FanName, ItemName=self.ItemName)
        source.addTask("TaskRemoveArrowAttach")
        source.addTask("TaskNodeRemoveFromParent", Node=ItemEntity)

        source.addTask("TaskObjectReturn", Object=ItemObject)
        source.addTask("TaskObjectSetPosition", Object=ItemObject, Value=Pos)
        source.addTask("TaskEnable", Object=ItemObject, Value=False)
        pass

    def _onSkip(self):
        pass
    pass