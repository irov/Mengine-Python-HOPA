from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.System import System

SCENE_EFFECT_MOVIE_OPEN = "Movie2_Open"
SCENE_EFFECT_MOVIE_CLOSE = "Movie2_Close"

class SystemAccounts(System):
    def __init__(self):
        super(SystemAccounts, self).__init__()
        self.MenuFade = 0.5

    def _onRun(self):
        self.addObserver(Notificator.onLoadAccounts, self.__onLoadAccounts)
        self.__runTaskChains()
        return True

    def __scopeOpen(self, source, group_name):
        source.addScope(self.__scopeSceneEffect, group_name, SCENE_EFFECT_MOVIE_OPEN)

    def __scopeClose(self, source, group_name):
        source.addScope(self.__scopeSceneEffect, group_name, SCENE_EFFECT_MOVIE_CLOSE)

    def __scopeSceneEffect(self, source, group_name, movie_name):
        if not GroupManager.hasObject(group_name, movie_name):
            return

        scene_effect_movie = GroupManager.getObject(group_name, movie_name)
        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addTask("TaskEnable", Object=scene_effect_movie, Value=True)
                guard_source_movie.addTask("TaskMovie2Play", Movie2=scene_effect_movie, Wait=True)
                guard_source_movie.addTask("TaskEnable", Object=scene_effect_movie, Value=False)

    def __completeNewAccount(self, current_account_id, click_slot_id):
        profile = GroupManager.getGroup("Profile")
        demon_profile = profile.getObject("Demon_Profile")

        demon_profile.setParam("Current", current_account_id)
        demon_profile.appendParam("Accounts", (click_slot_id, current_account_id))

        profile_new = GroupManager.getGroup("Profile_New")
        demon_profile_new = profile_new.getObject("Demon_ProfileNew")

        demon_profile_new.setParam("ClickSlotID", None)
        return True

    def __updatePlayerName(self):
        GroupManager.getObject("Menu_Background", "Demon_MenuGreeting").getEntity().updateText()

    def __deleteSelectAccount(self, current_account_id):
        invalid_account_id = current_account_id

        old_mute = Mengine.getCurrentAccountSetting("Mute")
        old_fullscreen = Mengine.getCurrentAccountSettingBool("Fullscreen")
        old_cursor = Mengine.getCurrentAccountSetting("Cursor")
        old_custom_cursor = Mengine.getCurrentAccountSetting("CustomCursor")
        old_music_volume = Mengine.getCurrentAccountSetting("MusicVolume")
        old_sound_volume = Mengine.getCurrentAccountSetting("SoundVolume")

        Mengine.selectDefaultAccount()

        Mengine.changeCurrentAccountSetting("Mute", old_mute)
        Mengine.changeCurrentAccountSetting("Fullscreen", unicode(old_fullscreen))
        Mengine.changeCurrentAccountSetting("Cursor", old_cursor)
        Mengine.changeCurrentAccountSetting("CustomCursor", old_custom_cursor)
        Mengine.changeCurrentAccountSetting("MusicVolume", old_music_volume)
        Mengine.changeCurrentAccountSetting("SoundVolume", old_sound_volume)

        Mengine.deleteAccount(invalid_account_id)

        profile = DemonManager.getDemon("Profile")

        accounts = profile.getParam("Accounts")

        for slotID, accountID in accounts[:]:
            if accountID == invalid_account_id:
                profile.delParam("Accounts", (slotID, accountID))
                break

    def __onRemoveAccount(self):
        if Mengine.getCurrentAccountSettingBool("GameComplete") is True:
            profile = GroupManager.getGroup("Profile")
            demon_profile = profile.getObject("Demon_Profile")

            account_id = demon_profile.getParam("Current")
            self.__deleteSelectAccount(account_id)

            demon_profile.setParam("Current", None)

            GroupManager.getObject("Menu_Background", "Demon_MenuGreeting").getEntity().updateText()

    def __runTaskChains(self):
        # ------------------------- New Profile ------------------------------------------------------------------------
        def __on_new_profile(source_new_profile, click_slot_id):
            with GuardBlockInput(source_new_profile) as guard_source:
                guard_source.addScope(self.__scopeClose, "Profile")
                guard_source.addTask("TaskSceneLayerGroupEnable", LayerName="Profile", Value=False)
                guard_source.addTask("TaskSceneLayerGroupEnable", LayerName="Profile_New", Value=True)
                with guard_source.addParallelTask(2) as (guard_source_movie_new_profile, guard_source_fade):
                    guard_source_movie_new_profile.addScope(self.__scopeOpen, "Profile_New")

                    guard_source_fade.addTask("AliasFadeIn", FadeGroupName="Fade", To=self.MenuFade, Time=250.0)
                guard_source.addTask("AliasFadeOut", FadeGroupName="Fade", From=self.MenuFade, Time=250.0)

            with source_new_profile.addRaceTask(2) as (source_create_account, source_cancel_create_account):
                source_create_account.addTask("TaskListener", ID=Notificator.onCreateNewProfile, Filter=Functor(self.__completeNewAccount, click_slot_id))

                source_create_account.addFunction(self.__updatePlayerName)

                source_create_account.addScope(self.__scopeClose, "Profile_New")
                source_create_account.addTask("TaskSceneLayerGroupEnable", LayerName="Profile_New", Value=False)

                source_create_account.addTask("TaskSceneLayerGroupEnable", LayerName="Difficulty", Value=True)

                with source_create_account.addParallelTask(2) as (guard_source_movie_difficulty, guard_source_fade):
                    guard_source_movie_difficulty.addScope(self.__scopeOpen, "Difficulty")
                    guard_source_movie_difficulty.addTask("AliasFadeIn", FadeGroupName="Fade", To=self.MenuFade, Time=250.0)

                    guard_source_fade.addTask("AliasFadeOut", FadeGroupName="Fade", To=self.MenuFade, Time=250.0)

                source_create_account.addTask("TaskListener", ID=Notificator.onSelectedDifficulty)
                source_create_account.addTask("TaskSceneLayerGroupEnable", LayerName="Difficulty", Value=False)
                source_create_account.addTask("AliasFadeOut", FadeGroupName="Fade", From=self.MenuFade, Time=250.0)

                source_create_account.addTask("TaskNotify", ID=Notificator.onProfileCreated)

                source_cancel_create_account.addTask("TaskMovie2ButtonClick", GroupName="Profile_New", Movie2ButtonName="Movie2Button_Cancel")
                with GuardBlockInput(source_cancel_create_account) as guard_source:
                    guard_source.addScope(self.__scopeClose, "Profile_New")
                    guard_source.addTask("TaskSceneLayerGroupEnable", LayerName="Profile_New", Value=False)
                    guard_source.addTask("TaskSceneLayerGroupEnable", LayerName="Profile", Value=True)
                    guard_source.addScope(self.__scopeOpen, "Profile")
            return True

        with self.createTaskChain(Name="Menu_NewProfile", GroupName="Menu_Background", Global=True, Repeat=True) as tc_new_profile:
            tc_new_profile.addTask("TaskScopeListener", ID=Notificator.onNewProfile, Scope=__on_new_profile)

        # ------------------------- Del Profile ------------------------------------------------------------------------
        self.ProfileOkInteractive = True
        with self.createTaskChain(Name="Menu_DelProfile", GroupName="Menu_Background", Global=True, Repeat=True) as tc_delete_profile:
            with tc_delete_profile.addRaceTask(2) as (tc_delete, tc_change):
                tc_delete.addTask("TaskListener", ID=Notificator.onProfileDelete)
                tc_change.addTask("TaskListener", ID=Notificator.onProfileChange)

            def __fun_rof(source):
                pass

            tc_delete_profile.addScope(__fun_rof)

        # ------------------------- Remove Account ---------------------------------------------------------------
        with self.createTaskChain(Name="RemoveAccount", Global=True, Repeat=True) as tc_remove_account:
            tc_remove_account.addTask("TaskListener", ID=Notificator.onRemoveAccount)
            tc_remove_account.addTask("TaskSceneInit", SceneName="Menu")
            with GuardBlockInput(tc_remove_account) as guard_source:
                guard_source.addTask("TaskFunction", Fn=self.__onRemoveAccount)
            tc_remove_account.addNoSkip()

    def __onLoadAccounts(self):
        demon_profile = GroupManager.getObject("Profile", "Demon_Profile")
        if demon_profile is not None:
            accounts_list = []

            accounts = Mengine.getAccounts()

            for accountID in accounts:
                default = Mengine.getAccountSettingBool(accountID, "Default")
                if default is True:
                    continue

                slot_id = Mengine.getAccountSettingUInt(accountID, "SlotID")
                if slot_id is None:
                    Trace.log("System", 0, "SystemAccounts.onAccountInitialize invalid get SlotID for account %s" % (accountID))
                    continue

                accounts_list.append((slot_id, accountID))

            demon_profile.setParam("Accounts", accounts_list)

            if Mengine.hasCurrentAccount() is True:
                default = Mengine.getCurrentAccountSettingBool("Default")
                if default is False:
                    account_name = Mengine.getCurrentAccountName()
                    demon_profile.setParam("Current", account_name)

        return False

    def _onStop(self):
        pass