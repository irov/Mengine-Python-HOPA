from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

from PlayFabFramework.Managers.GameManager import GameManager

class LoadingScene(BaseEntity):
    def __init__(self):
        super(LoadingScene, self).__init__()

    def _onPreparation(self):
        self.__setupArt()

    def __setupArt(self):
        self.content = self.object.getObject("Movie2_Content")

        self.reload_button = self.object.getObject("Movie2Button_ReloadButton")
        slot_button = self.content.getMovieSlot("reload_button")
        slot_button.addChild(self.reload_button.getEntityNode())
        self.reload_button.setEnable(False)

        self.progressbar = self.object.getObject("Movie2ProgressBar_ProgressBar")
        slot_progressbar = self.content.getMovieSlot("progressbar")
        slot_progressbar.addChild(self.progressbar.getEntityNode())

    def __setupValueFollower(self):
        def __update(value, progress_bar):
            progress_bar.setValue(value)
            if value == 100.0:
                Notification.notify(Notificator.onValueFollowerComplete)

        self.progress_bar_follower = Mengine.createValueFollowerLinear(0.0, 0.05, __update, self.progressbar)

    def __cleanValueFollower(self):
        if self.progress_bar_follower is not None:
            Mengine.destroyValueFollower(self.progress_bar_follower)
            self.progress_bar_follower = None

    def __addProgressValueFollower(self, progress):
        cur_value = self.progress_bar_follower.getFollow()
        new_value = cur_value + progress

        self.progress_bar_follower.setFollow(new_value)

    def _onActivate(self):
        self.__runTaskChain()

    def __runTaskChain(self):
        self.tc = TaskManager.createTaskChain()
        with self.tc as tc:
            tc.addScope(self.__scopeLoadFromServer)
            tc.addScope(self.__scopeCheckSuccessLoading)

    def __scopeLoadFromServer(self, source):
        def __scope_load_step_scope(_source, _step_scope, _semaphore_success_load):
            _isSuccess = Semaphore(False, "_isSuccessLoad")

            _source.addScope(_step_scope, isSuccessHolder=_isSuccess)
            with _source.addRaceTask(2) as (_tc_success, _tc_fail):
                _tc_fail.addDelay(5000)
                _tc_fail.addSemaphore(_semaphore_success_load, To=False)

                _tc_success.addSemaphore(_isSuccess, From=True)
                _tc_success.addSemaphore(_semaphore_success_load, To=True)

        authorization_method = GameManager.scopeAuthenticate

        load_steps_scopes = [(authorization_method, 25, self.__scopeLoadFailResolve, "AUTHENTICATE"), (GameManager.scopeGetAccountInfo, 25, self.__scopeLoadFailResolve, "ACCOUNT_INFO"), (GameManager.scopeLoadTitleDataFromServer, 25, self.__scopeVesion_FailResolve, "TITLE_DATA"), (GameManager.scopeLoadStatistics, 25, self.__scopeLoadFailResolve, "STATISTICS"), ]

        source.addFunction(self.__setupValueFollower)
        source.addFunction(GameManager.clearLoadDataCache)

        for step_scope, step_progress_value, scope_fail_resolve, tag in load_steps_scopes:
            semaphore_success_load = Semaphore(False, "SuccessLoad_{}".format(tag))

            with source.addRepeatTask() as (repeat, until):
                repeat.addScope(__scope_load_step_scope, step_scope, semaphore_success_load)
                repeat.addDelay(100)
                repeat.addScope(scope_fail_resolve)

                until.addSemaphore(semaphore_success_load, From=True)

            with source.addIfSemaphore(semaphore_success_load, True) as (tc_true, tc_false):
                tc_false.addScope(scope_fail_resolve)
                tc_false.addBlock()

            source.addFunction(self.__addProgressValueFollower, step_progress_value)

        source.addListener(Notificator.onValueFollowerComplete)
        source.addFunction(self.__cleanValueFollower)

        source.addFunction(self.__loadFromCache)
        source.addFunction(GameManager.clearLoadDataCache)

    def __scopeLoadFailResolve(self, source):
        source.addDisable(self.progressbar)
        source.addEnable(self.button_reload)
        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_reload)
        source.addDisable(self.button_reload)
        source.addFunction(self.__cleanValueFollower)
        source.addEnable(self.progressbar)

    def __scopeVesion_FailResolve(self, source):
        source.addDisable(self.progressbar)
        source.addPrin("__scopeVesion_FailResolve")  # source.addScope(PopUp.scope_Check_Version)  # todo add scope_Check_Version

    def __loadFromCache(self):
        account_info_cache = GameManager.getLoadDataCache("AccountInfo")

        self.loadAccountInfo(account_info_cache)

        statistics_cache = GameManager.getLoadDataCache("Statistics")
        self.loadStatistics(statistics_cache)

    def loadAccountInfo(self, account_info):
        title_info = account_info.get("TitleInfo", {})

        display_name = title_info.get("DisplayName")

        # if AndroidFacebook.isLoggedIn() is True:
        #     FacebookManager.s_is_login = True

        if display_name is not None:
            Mengine.changeCurrentAccountSetting("DisplayName", unicode(display_name))

    def loadStatistics(self, statistics):
        pass

    def __scopeCheckSuccessLoading(self, source):
        source.addNotify(Notificator.onLoadingFinishedSuccess)

    def _onDeactivate(self):
        pass