from Foundation.GroupManager import GroupManager
from HOPA.Entities.BoneBoard.BoneBoardManager import BoneBoardManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroBoneUse(MacroCommand):

    def _onValues(self, values):
        self.bone_string = values[0]

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        SocketName = BoneBoardManager.getItemName(self.bone_string)
        Group = "BonePlates"
        Object = GroupManager.getObject(Group, SocketName)
        Quest = self.addQuest(source, "BoneUse", SceneName=self.SceneName, GroupName=Group,
                              Object=Object, BoneKey=self.bone_string)
        with Quest as tc_quest:
            tc_quest.addTask("AliasBoneUsage", Bone=self.bone_string, SceneName=self.SceneName)
