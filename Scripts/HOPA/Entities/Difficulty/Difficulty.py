from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

from HOPA.Entities.Difficulty.DifficultyManager import DifficultyManager


class Difficulty(BaseEntity):

    def _onActivate(self):
        AccountName = Mengine.getCurrentAccountName()
        Difficulty = Mengine.getAccountSetting(AccountName, "Difficulty")

        self.difficulties = DifficultyManager.getDifficulties()

        if Difficulty == "" or Difficulty == u"" or Difficulty is None:
            startCheckBox = self.difficulties.values()[0]
        else:
            startCheckBox = self.difficulties[Difficulty]

        diffCount = len(self.difficulties)

        with TaskManager.createTaskChain(Name="Menu_Difficulty", GroupName="Difficulty") as tc:
            tc.addTask("TaskInteractive", ObjectName="Socket_Block", Value=True)
            for checkBox in self.difficulties.values():
                tc.addTask("TaskCheckBoxBlockState", CheckBox=checkBox, Value=False)
                tc.addTask("TaskSetParam", Object=checkBox, Param="State", Value=False)

            tc.addTask("TaskSetParam", Object=startCheckBox, Param="State", Value=True)
            tc.addTask("TaskCheckBoxBlockState", CheckBox=startCheckBox, Value=True)

            with tc.addRepeatTask() as (tc_diff, tc_ok):
                with tc_diff.addRaceTask(diffCount) as tc_diff:
                    for checkBox, tc_id in zip(self.difficulties.values(), tc_diff):
                        tc_id.addTask("TaskCheckBox", CheckBox=checkBox, Value=True)
                        tc_id.addTask("TaskCheckBoxBlockState", CheckBox=checkBox, Value=True)
                        for tempCheckBox in self.difficulties.values():
                            if tempCheckBox is checkBox:
                                continue

                            tc_id.addTask("TaskSetParam", Object=tempCheckBox, Param="State", Value=False)
                            tc_id.addTask("TaskCheckBoxBlockState", CheckBox=tempCheckBox, Value=False)

                tc_ok.addTask("TaskButtonClick", ButtonName="Button_OK")
                tc_ok.addTask("TaskFunction", Fn=self.__onChangeDifficulty)

            for CheckBox in self.difficulties.values():
                tc.addTask("TaskCheckBoxBlockState", CheckBox=CheckBox, Value=True)

            tc.addTask("TaskInteractive", ObjectName="Socket_Block", Value=False)
            tc.addTask("TaskNotify", ID=Notificator.onSelectedDifficulty)

    def __onChangeDifficulty(self):
        value = ""

        for id, checkBox in self.difficulties.items():
            if checkBox.getBlockState() is True:
                value = id

        strValue = str(value)
        Difficulty = unicode(strValue)

        Mengine.changeCurrentAccountSetting("Difficulty", unicode(Difficulty))

    def _onDeactivate(self):
        if TaskManager.existTaskChain("Menu_Difficulty") is True:
            TaskManager.cancelTaskChain("Menu_Difficulty")
