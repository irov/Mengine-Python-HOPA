from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from Notification import Notification


class ProfileNew(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "AccountID", Update=ProfileNew.__updateAccountID)
        Type.addAction(Type, "ClickSlotID")

    def __updateAccountID(self, newValue):
        if TaskManager.existTaskChain("MakeProfile"):
            TaskManager.cancelTaskChain("MakeProfile")
        Notification.notify(Notificator.onCreateNewProfile, newValue)

    def _onActivate(self):
        Profile_New = GroupManager.getGroup("Profile_New")
        Demon_EditBox_Name = Profile_New.getObject("Demon_EditBox_Name")
        Demon_EditBox_Entity = Demon_EditBox_Name.getEntity()

        CHEAT_SKIP_MENU_IF_USER_EXIST = DefaultManager.getDefaultBool("CHEAT_SKIP_MENU", False)
        if CHEAT_SKIP_MENU_IF_USER_EXIST:
            with TaskManager.createTaskChain(Name="ProfileNew", GroupName="Profile_New") as tc:
                tc.addFunction(self.__selectClickSlotID)
                tc.addScope(self.__checkProfile)
                return

        with TaskManager.createTaskChain(Name="ButtonBack", GroupName="Profile_New") as tc:
            accounts = Mengine.getAccounts()
            if len(accounts) <= 1:
                tc.addTask("TaskEnable", GroupName="Profile_New", ObjectName="Movie2Button_Cancel", Value=False)
                tc.addTask("TaskEnable", GroupName="Profile_New", ObjectName="Movie2Button_Ok", Value=False)
                tc.addTask("TaskEnable", GroupName="Profile_New", ObjectName="Movie2Button_Ok2", Value=True)
            else:
                tc.addTask("TaskEnable", GroupName="Profile_New", ObjectName="Movie2Button_Cancel", Value=True)
                tc.addTask("TaskEnable", GroupName="Profile_New", ObjectName="Movie2Button_Ok", Value=True)
                tc.addTask("TaskEnable", GroupName="Profile_New", ObjectName="Movie2Button_Ok2", Value=False)

        Name = u""
        if Mengine.existText("ID_NewPROFILE_DEFAULT_NAME") is True:
            Name = Mengine.getTextByKey("ID_NewPROFILE_DEFAULT_NAME")
        # updateCarriage

        with TaskManager.createTaskChain(Name="ProfileNew", GroupName="Profile_New") as tc:
            tc.addTask("TaskInteractive", GroupName="Profile_New", ObjectName="Socket_Block", Value=True)
            tc.addTask("TaskSetParam", ObjectName="Text_Message", Param="TextID", Value="ID_PROFILE_ENTER_NAME")
            # if Name != u"":
            #     tc.addTask("TaskFunction", Fn = Demon_EditBox_Name.setValueByDefault, Args = (Name, ))
            tc.addTask("TaskSetParam", ObjectName="Demon_EditBox_Name", Param="Value", Value=Name)
            tc.addFunction(Demon_EditBox_Entity.carriageEnd)

        semaphore = Semaphore(False, "semaphoreNotEmptyName")

        def __check_not_empty_name():
            if len(Demon_EditBox_Name.getParam("Value")) == 0:
                return
            semaphore.setValue(True)

        if Name != u"":
            with TaskManager.createTaskChain(Name="MakeProfile", GroupName="Profile_New", Repeat=True) as tc:
                tc.addTask("TaskInteractive", ObjectName="Movie2Button_Ok", Value=True)
                tc.addTask("TaskInteractive", ObjectName="Movie2Button_Ok2", Value=True)

                with tc.addRepeatTask() as (tc_do, tc_until):
                    with tc_do.addRaceTask(2) as (tc1, tc2):
                        tc1.addListener(Notificator.EditBoxEmpty)
                        tc1.addTask("TaskSetParam", ObjectName="Movie2Button_Ok", Param="Interactive", Value=0)
                        tc1.addTask("TaskSetParam", ObjectName="Movie2Button_Ok2", Param="Interactive", Value=0)

                        tc2.addListener(Notificator.EditBoxChange)
                        tc2.addTask("TaskSetParam", ObjectName="Movie2Button_Ok", Param="Interactive", Value=1)
                        tc2.addTask("TaskSetParam", ObjectName="Movie2Button_Ok2", Param="Interactive", Value=1)
                        pass

                    # tc_until.addTask("TaskButtonClick", ButtonName = "Button_Ok", AutoEnable = False)
                    with tc_until.addRepeatTask() as (tc_until_click, tc_until_click_until_name_not_empty):
                        with tc_until_click.addRaceTask(4) as (tc_until_click_ok, tc_until_click_ok2, tc_until_click_ok3, tc_until_click_out):
                            tc_until_click_ok.addTask("TaskMovie2ButtonClick", Movie2ButtonName="Movie2Button_Ok", AutoEnable=False)
                            tc_until_click_ok2.addTask("TaskMovie2ButtonClick", Movie2ButtonName="Movie2Button_Ok2", AutoEnable=False)
                            tc_until_click_out.addTask("TaskMovie2SocketClick", GroupName='Profile_New',
                                                       Movie2Name='Movie2_Background', SocketName="close")

                            tc_until_click_ok3.addTask("TaskKeyPress", Keys=[Mengine.KC_RETURN], isDown=True)
                        tc_until_click.addFunction(__check_not_empty_name)

                        tc_until_click_until_name_not_empty.addSemaphore(semaphore, From=True, To=False)

                    tc_until.addFunction(self.__selectClickSlotID)
                    tc_until.addScope(self.__checkProfile)
        else:
            with TaskManager.createTaskChain(Name="MakeProfile", GroupName="Profile_New", Repeat=True) as tc_repeat:
                with tc_repeat.addRaceTask(2) as (tc_empty, tc_edit):
                    tc_empty.addListener(Notificator.EditBoxEmpty)
                    tc_empty.addTask("TaskSetParam", ObjectName="Movie2Button_Ok", Param="Interactive", Value=0)
                    tc_empty.addTask("TaskSetParam", ObjectName="Movie2Button_Ok2", Param="Interactive", Value=0)

                    tc_edit.addListener(Notificator.EditBoxChange)

                    tc_edit.addTask("TaskSetParam", ObjectName="Movie2Button_Ok", Param="Interactive", Value=1)
                    tc_edit.addTask("TaskSetParam", ObjectName="Movie2Button_Ok2", Param="Interactive", Value=1)
                    # tc_edit.addTask("TaskButtonClick", ButtonName = "MovieButton_Ok", AutoEnable = False)
                    with tc_edit.addRaceTask(4) as (tc_edit_click_ok, tc_edit_click_ok2, tc_edit_click_ok3, tc_edit_click_out):
                        tc_edit_click_ok.addTask("TaskMovie2ButtonClick", Movie2ButtonName="Movie2Button_Ok", AutoEnable=False)
                        tc_edit_click_ok2.addTask("TaskMovie2ButtonClick", Movie2ButtonName="Movie2Button_Ok2", AutoEnable=False)
                        tc_edit_click_out.addTask("TaskMovie2SocketClick", GroupName='Profile_New',
                                                  Movie2Name='Movie2_Background', SocketName="close")
                        tc_edit_click_ok3.addTask("TaskKeyPress", Keys=[Mengine.KC_RETURN], isDown=True)

                    tc_edit.addFunction(self.__selectClickSlotID)
                    tc_edit.addScope(self.__checkProfile)

    def _onDeactivate(self):
        if TaskManager.existTaskChain("ProfileNew") is True:
            TaskManager.cancelTaskChain("ProfileNew")

        if TaskManager.existTaskChain("MakeProfile") is True:
            TaskManager.cancelTaskChain("MakeProfile")

    def __selectClickSlotID(self):
        accounts = Mengine.getAccounts()

        slots = []
        for AccountID in accounts:
            if Mengine.getAccountSettingBool(AccountID, "Default") is True:
                continue

            SlotID = Mengine.getAccountSettingUInt(AccountID, "SlotID")

            slots.append(SlotID)

        id = 0

        while (True):
            if id in slots:
                id += 1

                continue

            self.object.setParam("ClickSlotID", id)
            break

    def __checkProfile(self, scope):
        slotID = self.object.getParam("ClickSlotID")

        Profile_New = GroupManager.getGroup("Profile_New")
        Demon_EditBox_Name = Profile_New.getObject("Demon_EditBox_Name")

        Name = Demon_EditBox_Name.getParam("Value")
        Name = Name.strip()

        if Name == u"":
            # Name = Mengine.getTextByKey("ID_NewPROFILE_DEFAULT_NAME")
            Name = "debugAGENT"
            scope.addTask("TaskSetParam", ObjectName="Text_Message", Param="TextID", Value="ID_PROFILE_ENTER_NAME")
            scope.addTask("TaskSetParam", ObjectName="Demon_EditBox_Name", Param="Value", Value=Name)  # return

        accounts = Mengine.getAccounts()

        for accountID in accounts:
            if Mengine.getAccountSettingBool(accountID, "Default") is True:
                continue

            AccountName = Mengine.getAccountSetting(accountID, "Name")

            if Name.lower() == AccountName.lower():
                scope.addTask("TaskSetParam", ObjectName="Text_Message", Param="TextID", Value="ID_PROFILE_EXIST")
                return

        if slotID is not None:
            accountID = Mengine.createAccount()

            Mengine.selectAccount(accountID)

            Mengine.changeCurrentAccountSettingBool("Default", False)
            Mengine.changeCurrentAccountSetting("Name", unicode(Name))
            # Mengine.changeCurrentAccountSetting("Name", Name)
            Mengine.changeCurrentAccountSetting("SlotID", unicode(slotID))
            Mengine.changeCurrentAccountSetting("SessionSave", unicode(False))

            self.object.setAccountID(accountID)

        else:
            Mengine.changeCurrentAccountSetting("Name", Name)

            Notification.notify(Notificator.onCreateNewProfile, slotID)
