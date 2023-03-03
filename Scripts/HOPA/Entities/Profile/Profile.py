from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Profile.ProfileManager import ProfileManager
from Notification import Notification


class Profile(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "MaxCount")
        Type.addActionActivate(Type, "Current", Update=Profile._updateCurrent)
        Type.addActionActivate(Type, "Accounts",
                               Update=Profile._restoreAccounts,
                               Append=Profile._appendAccount,
                               Remove=Profile._removeAccount)
        pass

    def __init__(self):
        super(Profile, self).__init__()
        self.profiles = {}
        self.oldCurrent = None
        self.SelectProfile = "$SelectProfile"

    def _updateCurrent(self, value):
        if value is not None:
            self._activateSelectAccount()

    def _restoreAccounts(self, Accounts):
        for slotID in range(self.MaxCount):
            self.setDefaultTextAlias(slotID)
            pass

        for slotID, accountID in Accounts:
            self._enableButtonPlayerText(slotID, accountID)
            pass
        pass

    def _appendAccount(self, id, account):
        slotID, accountID = account

        self._enableButtonPlayerText(slotID, accountID)
        pass

    def _removeAccount(self, id, account, accounts):
        slotID, accountID = account

        self.setDefaultTextAlias(slotID)
        pass

    def _enableButtonPlayerText(self, slotID, accountID):
        Name = Mengine.getAccountSetting(accountID, "Name")
        Over = "_Over"
        textID = 'ID_SelectProfile'
        textID_Over = textID + Over
        Mengine.setTextAlias(self.SelectProfile + "_" + str(slotID), self.SelectProfile, textID)
        Mengine.setTextAlias(self.SelectProfile + "_" + str(slotID), self.SelectProfile + Over, textID_Over)

        Mengine.setTextAliasArguments(self.SelectProfile + "_" + str(slotID), self.SelectProfile, Name)
        Mengine.setTextAliasArguments(self.SelectProfile + "_" + str(slotID), self.SelectProfile + Over, Name)

    def setDefaultTextAlias(self, slotID):
        Over = "_Over"
        textID = 'ID_PROFILE_DEFAULT_NAME'
        textID_Over = textID + Over
        Mengine.removeTextAliasArguments(self.SelectProfile + "_" + str(slotID), self.SelectProfile)
        Mengine.removeTextAliasArguments(self.SelectProfile + "_" + str(slotID), self.SelectProfile + Over)
        Mengine.setTextAlias(self.SelectProfile + "_" + str(slotID), self.SelectProfile, textID)
        Mengine.setTextAlias(self.SelectProfile + "_" + str(slotID), self.SelectProfile + Over, textID_Over)

    def _onPreparation(self):
        pass

    def Setup_Slots(self, slotID):
        groupName = "Profile"
        selectButton = self.profiles[slotID].selectButton
        objectDemon = GroupManager.getObject(groupName, "Demon_Profile")
        MovieSlots = objectDemon.getObject("Movie2_MovieSlots")
        slot = MovieSlots.getMovieSlot("slot_" + str(slotID))
        node = selectButton.getEntityNode()
        selectButton.setTextAliasEnvironment("{}_{}".format(self.SelectProfile, str(slotID)))
        slot.addChild(node)  # pos=slot.getWorldPosition()  # node.setWorldPosition(pos)

    # Ruslan
    def Clean_Slots(self, slotID):
        selectButton = self.profiles[slotID].selectButton

        node = selectButton.getEntityNode()
        node.removeFromParent()  # node.onDestroy()  # AttributeError: 'Entity' object has no attribute 'onDestroy'

    def _onActivate(self):
        self.profiles = ProfileManager.getProfiles()
        for Id in self.profiles:
            self.Setup_Slots(Id)
            self.setDefaultTextAlias(Id)

        Accounts = self.object.getParam("Accounts")
        AccountIDs = [slotID for slotID, accountID in Accounts]

        NewSlotIDs = [slotID for slotID in range(self.MaxCount) if slotID not in AccountIDs]

        if len(NewSlotIDs) > 0:
            for values in self.profiles.values():
                bCreate = values.getCreateButton()
                if bCreate is not None:
                    self._clickButtonCreate(bCreate)
                    break
                    pass
                pass
            pass

        for slotID in NewSlotIDs:
            self._enableButtonNewProfile(slotID)
            pass

        currentSlotID = self.object.getSlotID(self.Current)

        if self.Current is not None and currentSlotID is not None:
            buttonSelectProfile = self.profiles[currentSlotID].getSelectButton()

            with TaskManager.createTaskChain(Group=self.object) as tc:
                tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="Block", Value=True)

            self._enableButtonDeleteProfile(currentSlotID)
            self._enableButtonEditProfile(currentSlotID)
            pass
        else:
            Default = Mengine.getCurrentAccountSettingBool("Default")

            if Default is False:
                Mengine.changeCurrentAccountSetting("InvalidLoad", u"True")
                pass
            pass

        ActiveSlotIDs = [slotID for slotID in range(self.MaxCount) if slotID in AccountIDs]

        for slotID in ActiveSlotIDs:
            if slotID == currentSlotID:
                continue
                pass

            self._enableButtonSelectProfile(slotID)
            pass
        self._disableUnactivatedButtons()
        pass

    def _disableUnactivatedButtons(self):
        currentSlotID = self.object.getSlotID(self.Current)

        for slotID in range(self.MaxCount):
            if slotID != currentSlotID:
                buttonEditProfile = self.profiles[slotID].getEditButton()
                if buttonEditProfile is None:
                    return
                    pass
                buttonDeleteProfile = self.profiles[slotID].getDeleteButton()

                TaskManager.runAlias("TaskEnable", None, Group=self.object, Object=buttonEditProfile, Value=False)
                TaskManager.runAlias("TaskSetParam", None, Group=self.object,
                                     Object=buttonDeleteProfile, Param="Interactive", Value=0)
                pass
            pass
        pass

    def _onDeactivate(self):
        Accounts = self.object.getParam("Accounts")
        AccountIDs = [slotID for slotID, accountID in Accounts]

        NewSlotIDs = [slotID for slotID in range(self.MaxCount) if slotID not in AccountIDs]

        for slotID in NewSlotIDs:
            self._disableButtonNewProfile(slotID)
            pass

        currentSlotID = self.object.getSlotID(self.Current)
        self._disableButtonDeleteProfile(currentSlotID)

        ActiveSlotIDs = (slotID for slotID in range(self.MaxCount) if slotID in AccountIDs)

        for slotID in ActiveSlotIDs:
            if slotID == currentSlotID:
                continue
                pass

            self._disableButtonSelectProfile(slotID)
            pass

        self._disableButtonCreate()

        currentSlotID = self.object.getSlotID(self.Current)
        if currentSlotID is not None:
            buttonSelectProfile = self.profiles[currentSlotID].getSelectButton()

            with TaskManager.createTaskChain(Group=self.object, ) as tc:
                tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="Block", Value=False)

        # Ruslan
        for id_ in self.profiles:
            # print '[Debug Profile] id = {}'.format(id_)
            self.Clean_Slots(id_)

    def scopeOpen(self, source, GropName):
        MovieName = "Movie2_Open"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def scopeClose(self, source, GropName):
        MovieName = "Movie2_Close"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def SceneEffect(self, source, GropName, MovieName):
        if GroupManager.hasObject(GropName, MovieName) is True:
            Movie = GroupManager.getObject(GropName, MovieName)
            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                    guard_source_movie.addTask("TaskEnable", Object=Movie, Value=True)
                    guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
                    guard_source_movie.addTask("TaskEnable", Object=Movie, Value=False)

                    # guard_source_fade.addTask('AliasFadeOut', FadeGroupName='Fade', From=0.5, Time=250.0)

    def _clickButtonCreate(self, buttonCreateProfile):
        with TaskManager.createTaskChain(Name="ProfileButtonCreate", Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=buttonCreateProfile)
            # if buttonCreateProfile.getType() == "ObjectButton":
            #     tc.addTask("TaskButtonClick", Button=buttonCreateProfile)
            # elif buttonCreateProfile.getType() == "ObjectMovie2Button":
            #     tc.addTask("TaskMovie2ButtonClick", Movie2Button=buttonCreateProfile)

            tc.addTask("TaskFunction", Fn=self._findNewProfile)

    def _disableButtonCreate(self):
        if TaskManager.existTaskChain("ProfileButtonCreate"):
            TaskManager.cancelTaskChain("ProfileButtonCreate")
            pass
        pass

    def _findNewProfile(self):
        Accounts = self.object.getParam("Accounts")
        AccountIDs = [slotID for slotID, accountID in Accounts]
        NewSlotIDs = [slotID for slotID in range(self.MaxCount) if slotID not in AccountIDs]
        for slotID in NewSlotIDs:
            self._openWindowPlayerNew(slotID)
            break
            pass
        pass

    def _enableButtonNewProfile(self, slotID):
        buttonSelectProfile = self.profiles[slotID].getSelectButton()
        with TaskManager.createTaskChain(Name="ProfileButtonNewPlayer_%s" % (slotID), Group=self.object, Repeat=True) as tc:
            if buttonSelectProfile.getType() == 'ObjectButton':
                tc.addTask("TaskButtonClick", Button=buttonSelectProfile)
            elif buttonSelectProfile.getType() == 'ObjectMovie2Button':
                tc.addTask("TaskMovie2ButtonClick", Movie2Button=buttonSelectProfile)
            tc.addTask("TaskFunction", Fn=self._openWindowPlayerNew, Args=(slotID,))
            pass

        with TaskManager.createTaskChain(Group=self.object) as tc:
            if buttonSelectProfile.getType() == 'ObjectButton':
                tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="BlockState", Value=False)
                # tc.addTask("TaskPrint", Value = "1")
                tc.addTask("TaskButtonSetState", Button=buttonSelectProfile, State="onUp")
            elif buttonSelectProfile.getType() == 'ObjectMovie2Button':
                tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="Block", Value=False)

    def _disableButtonNewProfile(self, slotID):
        buttonSelectProfile = self.profiles[slotID].getSelectButton()
        if TaskManager.existTaskChain("ProfileButtonNewPlayer_%s" % (slotID)):
            TaskManager.cancelTaskChain("ProfileButtonNewPlayer_%s" % (slotID))
            pass
        if buttonSelectProfile.getType() == 'ObjectButton':
            buttonSelectProfile.setState("onDown")
            buttonSelectProfile.setBlockState(True)

            pass

    def _enableButtonSelectProfile(self, slotID):
        buttonSelectProfile = self.profiles[slotID].getSelectButton()
        if TaskManager.existTaskChain("ProfileButtonSelectPlayer_%s" % (slotID)):
            return
            pass

        accID = self.getAccountID(slotID)

        with TaskManager.createTaskChain(Name="ProfileButtonSelectPlayer_%s" % (slotID), Group=self.object, Repeat=True) as tc:
            if buttonSelectProfile.getType() == 'ObjectButton':
                tc.addTask("TaskButtonClick", Button=buttonSelectProfile)
                # tc.addTask("TaskPrint", Value = "2")
                tc.addTask("TaskButtonSetState", Button=buttonSelectProfile, State="onDown")
                tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="BlockState", Value=True)
            elif buttonSelectProfile.getType() == 'ObjectMovie2Button':
                tc.addTask("TaskMovie2ButtonClick", Movie2Button=buttonSelectProfile)
                tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="Block", Value=True)
            tc.addTask("TaskSetParam", Object=self.object, Param="Current", Value=accID)

    def _disableButtonSelectProfile(self, slotID):
        if TaskManager.existTaskChain("ProfileButtonSelectPlayer_%s" % (slotID)):
            TaskManager.cancelTaskChain("ProfileButtonSelectPlayer_%s" % (slotID))
            pass
        pass

    def _enableButtonDeleteProfile(self, slotID):
        buttonDeleteProfile = self.profiles[slotID].getDeleteButton()
        MessageGroup = GroupManager.getGroup("Message")
        ProfileGroup = GroupManager.getGroup("Profile")

        CurrentSceneName = SceneManager.getCurrentSceneName()

        if TaskManager.existTaskChain("ProfileButtonDeletePlayer_%s" % (slotID)):
            return
            pass

        with TaskManager.createTaskChain(Name="ProfileButtonDeletePlayer_%s" % (slotID), Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskSetParam", Group=self.object, Object=buttonDeleteProfile, Param="Interactive", Value=1)
            if buttonDeleteProfile.getType() == 'ObjectButton':
                tc.addTask("TaskButtonClick", Button=buttonDeleteProfile)
            elif buttonDeleteProfile.getType() == 'ObjectMovie2Button':
                tc.addTask("TaskMovie2ButtonClick", Movie2Button=buttonDeleteProfile)

            # if ProfileGroup.hasObject("Movie2_Close"):
            #     with GuardBlockInput(tc) as guard_tc:
            #         guard_tc.addTask("TaskMovie2Play", GroupName = "Profile", Movie2Name = "Movie2_Close", Wait = True)
            #         pass
            #     pass
            tc.addScope(self.scopeClose, "Profile")

            tc.addTask("AliasMessageShow", TextID="ID_POPUP_PROFILE_DELETE")

            # if MessageGroup.hasObject("Movie_Open") is True:
            #     with GuardBlockInput(tc) as guard_tc:
            #         guard_tc.addTask("TaskMoviePlay", GroupName = "Message", MovieName = "Movie_Open", Wait = True)
            #         pass
            #     pass

            with tc.addRaceTask(2) as (tc_no, tc_yes):
                tc_no.addTask("AliasMessageNo")
                # if MessageGroup.hasObject("Movie_Close") is True:
                #     with GuardBlockInput(tc_no) as guard_tc:
                #         guard_tc.addTask("TaskMoviePlay", GroupName = "Message", MovieName = "Movie_Close", Wait = True)
                #         pass
                #     pass
                tc_no.addTask("AliasMessageHide", SceneName=CurrentSceneName)

                # if ProfileGroup.hasObject("Movie2_Open"):
                #     with GuardBlockInput(tc_no) as guard_tc:
                #         guard_tc.addTask("TaskMovie2Play", GroupName = "Profile", Movie2Name = "Movie2_Open", Wait = True)
                #         pass
                #     pass
                tc_no.addScope(self.scopeOpen, "Profile")
                tc_yes.addTask("AliasMessageYes")
                tc_yes.addTask("AliasMessageHide", SceneName=CurrentSceneName)

                tc_yes.addTask("TaskFunction", Fn=self._deleteSelectAccount, Args=(slotID,))
                pass
            pass
        pass

    def _disableButtonDeleteProfile(self, slotID):
        if slotID is None:
            return
            pass
        buttonDeleteProfile = self.profiles[slotID].getDeleteButton()

        if TaskManager.existTaskChain("ProfileButtonDeletePlayer_%s" % (slotID)):
            TaskManager.cancelTaskChain("ProfileButtonDeletePlayer_%s" % (slotID))
            TaskManager.runAlias("TaskSetParam", None, Group=self.object, Object=buttonDeleteProfile,
                                 Param="Interactive", Value=0)
            pass
        pass

    def _enableButtonEditProfile(self, slotID):
        buttonEditProfile = self.profiles[slotID].getEditButton()
        if buttonEditProfile is None:
            return
            pass

        if TaskManager.existTaskChain("ProfileButtonEditPlayer_%s" % (slotID)):
            return
            pass

        Profile_NewGroup = GroupManager.getGroup("Profile_New")

        with TaskManager.createTaskChain(Name="ProfileButtonEditPlayer_%s" % (slotID), Group=self.object,
                                         Repeat=True) as tc:
            tc.addTask("TaskEnable", Group=self.object, Object=buttonEditProfile, Value=True)
            if buttonEditProfile.getType() == 'ObjectButton':
                tc.addTask("TaskButtonClick", Button=buttonEditProfile)
            elif buttonEditProfile.getType() == 'ObjectMovie2Button':
                tc.addTask("TaskMovie2ButtonClick", Movie2Button=buttonEditProfile)

            tc.addTask("TaskSceneLayerGroupEnable", LayerName="Profile_New", Value=True)

            # if Profile_NewGroup.hasObject("Movie2_Open"):
            #     with GuardBlockInput(tc) as guard_tc:
            #         guard_tc.addTask("TaskMovie2Play", GroupName = "Profile_New", Movie2Name = "Movie2_Open", Wait = True)
            #         pass
            #     pass
            tc.addScope(self.scopeOpen, "Profile_New")

            with tc.addRaceTask(2) as (tc_until_0, tc_until_1):
                if GroupManager.hasObject('Profile_New', 'Button_Back'):
                    tc_until_0.addTask("TaskButtonClick", GroupName="Profile_New", ButtonName="Button_Back")
                elif GroupManager.hasObject('Profile_New', 'MovieButton_Back'):
                    tc_until_0.addTask("TaskMovieButtonClick", GroupName="Profile_New", MovieButtonName="MovieButton_Back")

                tc_until_1.addTask("TaskListener", ID=Notificator.onCreateNewProfile)
                pass

            # if Profile_NewGroup.hasObject("Movie2_Close"):
            #     with GuardBlockInput(tc) as guard_tc:
            #         guard_tc.addTask("TaskMovie2Play", GroupName = "Profile_New", Movie2Name = "Movie2_Close", Wait = True)
            #         pass
            #     pass
            tc.addScope(self.scopeClose, "Profile_New")

            tc.addTask("TaskSceneLayerGroupEnable", LayerName="Profile_New", Value=False)
            tc.addTask("TaskFunction", Fn=self._updateButtonPlayerText, Args=(slotID,))
            pass
        pass

    def _disableButtonEditProfile(self, slotID):
        buttonEditProfile = self.profiles[slotID].getEditButton()
        if buttonEditProfile is None:
            return
            pass

        if TaskManager.existTaskChain("ProfileButtonEditPlayer_%s" % (slotID)):
            TaskManager.cancelTaskChain("ProfileButtonEditPlayer_%s" % (slotID))
            TaskManager.runAlias("TaskEnable", None, Group=self.object, Object=buttonEditProfile, Value=False)
            pass
        pass

    def _updateButtonPlayerText(self, slotID):
        accountID = self.getAccountID(slotID)
        buttonSelectProfile = self.profiles[slotID].getSelectButton()
        textID = 'ID_SelectProfile'
        Name = Mengine.getAccountSetting(accountID, "Name")
        if buttonSelectProfile.getType() == 'ObjectButton':
            buttonSelectProfile.setParam("TextID", textID)
            buttonSelectProfile.setTextArgs((Name,))
        elif buttonSelectProfile.getType() == 'ObjectMovie2Button':
            self.setDefaultTextAlias(slotID)
        pass

    def getAccountID(self, _slotID):
        Accounts = self.object.getParam("Accounts")
        for slotID, accountID in Accounts:
            if slotID == _slotID:
                return accountID
                pass
            pass

        return None
        pass

    def getSlotID(self, accID):
        Accounts = self.object.getParam("Accounts")
        for slotID, accountID in Accounts:
            if accountID == accID:
                return slotID
                pass
            pass

        return None
        pass

    def _openWindowPlayerNew(self, clickSlotID, closeProfile=True):
        Profile_NewGroup = GroupManager.getGroup("Profile_New")
        Demon_ProfileNew = Profile_NewGroup.getObject("Demon_ProfileNew")

        Demon_ProfileNew.setParam("ClickSlotID", clickSlotID)

        Notification.notify(Notificator.onNewProfile, clickSlotID)
        pass

    def _activateSelectAccount(self):
        currentSlotID = self.object.getSlotID(self.Current)
        if self.oldCurrent == currentSlotID:
            return
            pass

        if self.oldCurrent is not None:
            buttonSelectProfile = self.profiles[self.oldCurrent].getSelectButton()

            self._enableButtonSelectProfile(self.oldCurrent)
            self._disableButtonDeleteProfile(self.oldCurrent)
            self._disableButtonEditProfile(self.oldCurrent)

            with TaskManager.createTaskChain(Group=self.object, ) as tc:
                if buttonSelectProfile.getType() == 'ObjectButton':
                    tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="BlockState", Value=False)
                    # tc.addTask("TaskPrint", Value = "3")
                    tc.addTask("TaskButtonSetState", Button=buttonSelectProfile, State="onUp")
                elif buttonSelectProfile.getType() == 'ObjectMovie2Button':
                    tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="Block", Value=False)

        self._disableButtonSelectProfile(currentSlotID)
        self._enableButtonDeleteProfile(currentSlotID)
        self._enableButtonEditProfile(currentSlotID)
        self.oldCurrent = currentSlotID

        Notification.notify(Notificator.onProfileChange, currentSlotID)
        pass

    def _deleteSelectAccount(self, slotID):
        self.setDefaultTextAlias(slotID)

        accountID = self.object.getAccountID(slotID)
        Old_Mute = Mengine.getCurrentAccountSetting("Mute")
        Old_Fullscreen = Mengine.getCurrentAccountSettingBool("Fullscreen")
        Old_Widescreen = Mengine.getCurrentAccountSetting("Widescreen")
        Old_Cursor = Mengine.getCurrentAccountSetting("Cursor")
        Old_CustomCursor = Mengine.getCurrentAccountSetting("CustomCursor")
        Old_MusicVolume = Mengine.getCurrentAccountSetting("MusicVolume")
        Old_SoundVolume = Mengine.getCurrentAccountSetting("SoundVolume")
        Old_VoiceVolume = Mengine.getCurrentAccountSetting("VoiceVolume")

        self._disableButtonDeleteProfile(slotID)

        self._disableButtonEditProfile(slotID)

        self._enableButtonNewProfile(slotID)

        if TaskManager.existTaskChain("ProfileButtonCreate") is False:
            for values in self.profiles.values():
                bCreate = values.getCreateButton()

                if bCreate is not None:
                    self._clickButtonCreate(bCreate)
                    break
                    pass
                pass
            pass

        self.oldCurrent = None
        self.object.delParam("Accounts", (slotID, accountID))
        self.object.setParam("Current", None)

        Mengine.selectDefaultAccount()

        Mengine.changeCurrentAccountSetting("Mute", Old_Mute)
        Mengine.changeCurrentAccountSetting("Fullscreen", unicode(Old_Fullscreen))
        Mengine.changeCurrentAccountSetting("Widescreen", Old_Widescreen)
        Mengine.changeCurrentAccountSetting("Cursor", Old_Cursor)
        Mengine.changeCurrentAccountSetting("CustomCursor", Old_CustomCursor)
        Mengine.changeCurrentAccountSetting("MusicVolume", Old_MusicVolume)
        Mengine.changeCurrentAccountSetting("SoundVolume", Old_SoundVolume)
        Mengine.changeCurrentAccountSetting("VoiceVolume", Old_VoiceVolume)

        Mengine.deleteAccount(accountID)
        accounts = Mengine.getAccounts()
        ProfileGroup = self.object.getGroup()

        GroupManager.getObject("Menu_Background", "Demon_MenuGreeting").getEntity().updateText()

        if len(accounts) <= 1:
            # if ProfileGroup.hasObject("Movie2_Open") is True:
            with TaskManager.createTaskChain(Group=self.object, ) as tc:
                #         with GuardBlockInput(tc) as guard_tc:
                #             guard_tc.addTask("TaskMovie2Play", GroupName = "Profile", Movie2Name = "Movie2_Open", Wait = True)
                #             # guard_tc.addTask("TaskNotify", ID = Notificator.onProfileDelete)
                #             pass
                #         pass
                #     pass
                tc.addScope(self.scopeOpen, "Profile")
                tc.addTask("TaskNotify", ID=Notificator.onProfileDelete)
            self._openWindowPlayerNew(0, False)
            pass
        else:
            if ProfileGroup.hasObject("Movie2_Open") is True:
                with TaskManager.createTaskChain(Group=self.object, ) as tc:
                    with GuardBlockInput(tc) as guard_tc:
                        # guard_tc.addTask("TaskMovie2Play", GroupName = "Profile", Movie2Name = "Movie2_Open", Wait = True)
                        guard_tc.addScope(self.scopeOpen, "Profile")
                        guard_tc.addTask("TaskNotify", ID=Notificator.onProfileDelete)
                        pass
                    pass
                pass

            Accounts = self.object.getParam("Accounts")

            for slotID, accID in Accounts:
                self._disableButtonNewProfile(slotID)
                with TaskManager.createTaskChain() as tc:
                    tc.addTask("TaskSetParam", Object=self.object, Param="Current", Value=accID)
                break

            currentSlotID = self.object.getSlotID(self.Current)

            if self.Current is not None and currentSlotID is not None:
                buttonSelectProfile = self.profiles[currentSlotID].getSelectButton()

                with TaskManager.createTaskChain(Group=self.object) as tc:
                    tc.addTask("TaskSetParam", Object=buttonSelectProfile, Param="Block", Value=True)
