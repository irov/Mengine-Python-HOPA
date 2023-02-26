import Trace
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Difficulty2.Difficulty2Manager import Difficulty2Manager

HAS_ITEM_PLUS = SystemManager.hasSystem('SystemItemPlusScene')

class Difficulty2(BaseEntity):
    def __init__(self):
        super(Difficulty2, self).__init__()

        self.SystemDifficultyInstance = None

        self.difficulties = None
        self.difficultiesParams = None
        self.difficultiesScrollbars = None

        self.currentDifficultyId = None

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

    def loadSavedCustomDiffParam(self):
        """
        load custom difficulty saved eariler paramteters from mengine
        (need to call only if custom difficulty was set earlier for player profile
         when this method called and custom difficulty wasn't changed, then paramters from xlsx
         will be ignored and will be loaded default hardcoded Custom Difficulty params)
        """

        # setup difficulty scrollbars params
        diffScrollbarParams = self.difficultiesScrollbars["Custom"]

        diffScrollbarParams["Hint"].setTime(self.SystemDifficultyInstance.fHintTime)

        diffScrollbarParams["Skip"].setTime(self.SystemDifficultyInstance.fSkipTime)

        # setup difficulty checkbox params
        diffCheckboxParams = self.difficultiesParams["Custom"]

        diffCheckboxParams["SPARKLES_ON_ACTIVE_AREAS"][0] = self.SystemDifficultyInstance.bSparkOnActiveArea

        diffCheckboxParams["TUTORIAL_AVAILABLE"][0] = self.SystemDifficultyInstance.bTutorialAvaliable

        if HAS_ITEM_PLUS:
            diffCheckboxParams["PLUS_ITEM_INDICATED"][0] = self.SystemDifficultyInstance.bItemPlusIndicator

        diffCheckboxParams["CHANGE_ICON_ON_ACTIVE_AREAS"][0] = self.SystemDifficultyInstance.bChangeActiveAreaIcon

        diffCheckboxParams["INDICATORS_ON_MAP"][0] = self.SystemDifficultyInstance.bMapIndicator

        diffCheckboxParams["SPARKLES_ON_HO"][0] = self.SystemDifficultyInstance.bSparksOnHO

    def setScrollbarsTexts(self):
        movieSlots = GroupManager.getObject('Difficulty', 'Movie2_Slots')
        movieSlotsEntity = movieSlots.getEntity()

        if movieSlotsEntity is not None:
            diffScrollbarParams = self.difficultiesScrollbars[self.currentDifficultyId]

            hintScrollbarData = diffScrollbarParams["Hint"]
            hintTimeSec = int(hintScrollbarData.getTime())
            maxHintTimeSec = int(hintScrollbarData.getTimeMax())

            if movieSlotsEntity.hasMovieText("ID_HintTimeDiffTwoArgs"):
                textHint = movieSlotsEntity.getMovieText('ID_HintTimeDiffTwoArgs')
                textHint.setTextFormatArgs(hintTimeSec, maxHintTimeSec)
            elif movieSlotsEntity.hasMovieText("ID_HintTimeDiff"):
                textHint = movieSlotsEntity.getMovieText("ID_HintTimeDiff")
                textHint.setTextFormatArgs(hintTimeSec)
                Trace.log("Entity", 5, '[Difficulty] in movie {}: ID_HintTimeDiff="%s/500" is deprecated, change to ID_HintTimeDiffTwoArgs="%s/%s"'.format(movieSlots.getName()))
            else:
                Trace.log("Entity", 5, '[Difficulty] in movie {}: NOT FOUND TEXT! add ID_HintTimeDiff="%s/500" or ID_HintTimeDiffTwoArgs="%s/%s"'.format(movieSlots.getName()))

            skipScrollbarData = diffScrollbarParams["Skip"]
            skipTimeSec = int(skipScrollbarData.getTime())
            maxSkipTimeSec = int(skipScrollbarData.getTimeMax())

            if movieSlotsEntity.hasMovieText("ID_SkipTimeDiffTwoArgs"):
                textSkip = movieSlotsEntity.getMovieText('ID_SkipTimeDiffTwoArgs')
                textSkip.setTextFormatArgs(skipTimeSec, maxSkipTimeSec)
            elif movieSlotsEntity.hasMovieText("ID_SkipTimeDiff"):
                textSkip = movieSlotsEntity.getMovieText('ID_SkipTimeDiff')
                textSkip.setTextFormatArgs(skipTimeSec)
                Trace.log("Entity", 5, '[Difficulty] in movie {}: ID_SkipTimeDiff="%s/500" is deprecated, change to ID_SkipTimeDiffTwoArgs="%s/%s"'.format(movieSlots.getName()))
            else:
                Trace.log("Entity", 5, '[Difficulty] in movie {}: NOT FOUND TEXT! add ID_SkipTimeDiff="%s/500" or ID_SkipTimeDiffTwoArgs="%s/%s"'.format(movieSlots.getName()))

    def __handleMengineSettings(self):
        # difficulty scrollbars
        difficultyScrollbarsData = self.difficultiesScrollbars[self.currentDifficultyId]

        fHintTime = difficultyScrollbarsData["Hint"].getTime()
        Mengine.changeCurrentAccountSetting("DifficultyCustomHintTime", unicode(int(fHintTime * 1000.0)))  # ms

        fSkipTime = difficultyScrollbarsData["Skip"].getTime()
        Mengine.changeCurrentAccountSetting("DifficultyCustomSkipTime", unicode(int(fSkipTime * 1000.0)))  # ms

        # difficulty checkboxes
        diffCheckBoxParam = self.difficultiesParams[self.currentDifficultyId]

        bSparksActiveArea = diffCheckBoxParam["SPARKLES_ON_ACTIVE_AREAS"][0]
        Mengine.changeCurrentAccountSetting("DifficultyCustomSparklesOnActiveAreas", unicode(bSparksActiveArea))

        bTutorialAvailable = diffCheckBoxParam["TUTORIAL_AVAILABLE"][0]
        Mengine.changeCurrentAccountSetting("DifficultyCustomTutorial", unicode(bTutorialAvailable))

        bItemPlusIndicator = False
        if HAS_ITEM_PLUS:
            bItemPlusIndicator = diffCheckBoxParam["PLUS_ITEM_INDICATED"][0]
            Mengine.changeCurrentAccountSetting("DifficultyCustomPlusItemIndicated", unicode(bItemPlusIndicator))

        bChangeIconActiveArea = diffCheckBoxParam["CHANGE_ICON_ON_ACTIVE_AREAS"][0]
        Mengine.changeCurrentAccountSetting("DifficultyCustomChangeIconOnActiveAreas", unicode(bChangeIconActiveArea))

        bMapIndicator = diffCheckBoxParam["INDICATORS_ON_MAP"][0]
        Mengine.changeCurrentAccountSetting("DifficultyCustomIndicatorsOnMap", unicode(bMapIndicator))

        bSparksOnHO = diffCheckBoxParam["SPARKLES_ON_HO"][0]
        Mengine.changeCurrentAccountSetting("DifficultyCustomSparklesOnHOPuzzles", unicode(bSparksOnHO))

        # save to system, so each account has it's own custom settings
        if self.SystemDifficultyInstance is not None:
            self.SystemDifficultyInstance.fSkipTime = fSkipTime
            self.SystemDifficultyInstance.fHintTime = fHintTime

            self.SystemDifficultyInstance.bSparkOnActiveArea = bSparksActiveArea
            self.SystemDifficultyInstance.bTutorialAvaliable = bTutorialAvailable
            self.SystemDifficultyInstance.bChangeActiveAreaIcon = bChangeIconActiveArea
            self.SystemDifficultyInstance.bMapIndicator = bMapIndicator
            self.SystemDifficultyInstance.bSparksOnHO = bSparksOnHO

            if HAS_ITEM_PLUS:
                self.SystemDifficultyInstance.bItemPlusIndicator = bItemPlusIndicator

        # currentDifficultyId: Casual, Normal, Expert, Custom
        Mengine.changeCurrentAccountSetting("Difficulty", unicode(str(self.currentDifficultyId)))

    def _onPreparation(self):
        super(Difficulty2, self)._onPreparation()

        self.currentDifficultyId = Mengine.getCurrentAccountSetting("Difficulty")

        self.difficulties, self.difficultiesParams, self.difficultiesScrollbars = Difficulty2Manager.getDifficulties()

        self.SystemDifficultyInstance = SystemManager.getSystem("SystemDifficulty")
        if self.SystemDifficultyInstance is not None:
            if self.SystemDifficultyInstance.bIsCustomDifficultySetOnce:
                self.loadSavedCustomDiffParam()

        self.__handleMengineSettings()

        self.setScrollbarsTexts()

    def updateDifficultyParams(self):
        # update checkboxes
        difficultyCheckBoxParams = self.difficultiesParams[self.currentDifficultyId]
        for checkboxVal, checkbox in difficultyCheckBoxParams.itervalues():
            if checkbox is not None:
                checkbox.setValue(checkboxVal)

        # update scrollbars
        difficultyScrollbarParams = self.difficultiesScrollbars[self.currentDifficultyId]

        for scrollbarData in difficultyScrollbarParams.itervalues():
            scrollbar_obj = scrollbarData.getScrollbarObject()
            scrollbar_entity = scrollbar_obj.getEntity()
            scrollbar_entity.set_percentage(scrollbarData.getTimeNormalized())

    def setCurrentDifficultyId(self, difficultyId):
        self.currentDifficultyId = difficultyId

        if self.currentDifficultyId == "Custom":
            self.SystemDifficultyInstance = SystemManager.getSystem("SystemDifficulty")
            if self.SystemDifficultyInstance is not None:
                self.SystemDifficultyInstance.bIsCustomDifficultySetOnce = True

    def setCurrentDifficulty(self, newDifficultyCheckbox, difficultyId):
        if newDifficultyCheckbox is None:
            return

        for difficultyCheckbox in self.difficulties.values():
            difficultyCheckbox.setValue(False)
            difficultyCheckbox.setBlockState(False)

        newDifficultyCheckbox.setValue(True)
        newDifficultyCheckbox.setBlockState(True)

        self.setCurrentDifficultyId(difficultyId)

        self.updateDifficultyParams()

    def __handleClickCheckbox(self, prevDifficultyId, clickedCheckBoxId):
        # refresh all check boxes
        curDifficultyCheckboxParams = self.difficultiesParams[self.currentDifficultyId]

        prevDifficultyCheckboxParams = self.difficultiesParams[prevDifficultyId]

        # replicate prev difficulty checkbox values to current("Custom") difficulty checkbox values
        for checkboxId, (checkboxVal, checkbox) in prevDifficultyCheckboxParams.iteritems():
            curDifficultyCheckboxParams[checkboxId][0] = checkboxVal

        # revert clicked checkbox value
        clickedCheckBoxValue = curDifficultyCheckboxParams[clickedCheckBoxId][0]
        curDifficultyCheckboxParams[clickedCheckBoxId][0] = not clickedCheckBoxValue

    def scopeChangeCheckBoxParam(self, source):
        prevDifficultyId = self.currentDifficultyId

        for (checkboxId, (checkboxVal, checkbox)), race in source.addRaceTaskList(self.difficultiesParams[prevDifficultyId].iteritems()):
            if checkbox is None:
                race.addBlock()
                continue

            race.addTask("TaskMovie2CheckBox", Movie2CheckBox=checkbox, Value=not checkboxVal)

            # force difficulty to be custom after one of param is changed
            race.addFunction(self.setCurrentDifficulty, self.difficulties['Custom'], 'Custom')

            race.addFunction(self.__handleClickCheckbox, prevDifficultyId, checkboxId)
            race.addFunction(self.updateDifficultyParams)

    def __onScrollbarEventScroll(self, percentageVal, scrolledScrollbarId):
        # copy difficulty parameters from current difficulty to "Custom"
        currentDifficultyCheckboxParams = self.difficultiesParams[self.currentDifficultyId]
        customDifficultyCheckboxParams = self.difficultiesParams["Custom"]
        for checkboxId, (checkboxVal, checkbox) in currentDifficultyCheckboxParams.iteritems():
            customDifficultyCheckboxParams[checkboxId][0] = checkboxVal

        # copy scrollbars difficulty parameters from current difficulty to "Custom"
        currentDifficultyScrollbarParams = self.difficultiesScrollbars[self.currentDifficultyId]
        customDifficultyScrollbarParams = self.difficultiesScrollbars["Custom"]
        for ScrollbarId, ScrollbarData in currentDifficultyScrollbarParams.iteritems():
            customDifficultyScrollbarParams[ScrollbarId].setTime(ScrollbarData.getTime())

        # force difficulty to be custom
        self.setCurrentDifficulty(self.difficulties["Custom"], "Custom")

        # current scrolled Scrollbar update percentage
        scrolledScrollbarData = self.difficultiesScrollbars["Custom"][scrolledScrollbarId]
        scrolledScrollbarData.setTimeNormalized(percentageVal)
        scrollbar_obj = scrolledScrollbarData.getScrollbarObject()
        scrollbar_entity = scrollbar_obj.getEntity()
        scrollbar_entity.set_percentage(percentageVal)

        # update text
        self.setScrollbarsTexts()

    def setObservers(self):
        for scrollbarId, scrollbarData in self.difficultiesScrollbars['Custom'].iteritems():
            scrollbar_obj = scrollbarData.getScrollbarObject()
            scrollbar_obj.onScroll.addObserver(self.__onScrollbarEventScroll, scrollbarId)

    def scopeClose(self, source):
        GropName = "Difficulty"
        MovieName = "Movie2_Close"

        if GroupManager.hasObject(GropName, MovieName) is True:
            Movie = GroupManager.getObject(GropName, MovieName)

            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                    guard_source_movie.addTask("TaskEnable", Object=Movie, Value=True)
                    guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
                    guard_source_movie.addTask("TaskEnable", Object=Movie, Value=False)

    def setBottomButtons(self, ok2Exists):
        if not ok2Exists:
            return

        cancelButton = GroupManager.getObject('Difficulty', 'Movie2Button_Cancel')
        okButton = GroupManager.getObject('Difficulty', 'Movie2Button_OK')
        ok2Button = GroupManager.getObject('Difficulty', 'Movie2Button_OK2')

        fromMainMenu = SceneManager.getCurrentSceneName() == "Menu"

        cancelButton.setEnable(not fromMainMenu)
        okButton.setEnable(not fromMainMenu)
        ok2Button.setEnable(fromMainMenu)

    def _onRestore(self):
        ok2Exists = GroupManager.hasObject('Difficulty', 'Movie2Button_OK2')
        self.setBottomButtons(ok2Exists)

    def _onActivate(self):
        super(Difficulty2, self)._onActivate()

        AccountName = Mengine.getCurrentAccountName()
        Difficulty = Mengine.getAccountSetting(AccountName, "Difficulty")

        if Difficulty == "" or Difficulty == u"" or Difficulty is None:
            startCheckBox = self.difficulties.values()[0]
        else:
            startCheckBox = self.difficulties[Difficulty]

        ok2Exists = GroupManager.hasObject('Difficulty', 'Movie2Button_OK2')
        self.setBottomButtons(ok2Exists)

        with TaskManager.createTaskChain(Name="Menu_Difficulty", GroupName="Difficulty") as tc:
            tc.addTask('TaskInteractive', ObjectName='Socket_Block', Value=True)
            tc.addFunction(self.setObservers)

            for checkbox in self.difficulties.itervalues():
                tc.addTask('TaskCheckBoxBlockState', CheckBox=checkbox, Value=False)
                tc.addTask('TaskSetParam', Object=checkbox, Param='Value', Value=False)

            tc.addTask('TaskSetParam', Object=startCheckBox, Param='Value', Value=True)
            tc.addTask('TaskCheckBoxBlockState', CheckBox=startCheckBox, Value=True)

            tc.addDelay(0.0)  # one frame delay

            tc.addFunction(self.updateDifficultyParams)

            # main loop

            with tc.addRepeatTask() as (repeat, until):
                with repeat.addRaceTask(2) as (race_0, race_1):
                    # handle change param of difficulty preset
                    race_0.addScope(self.scopeChangeCheckBoxParam)

                    # choose difficulty preset
                    for (difficultyId, checkbox), race in race_1.addRaceTaskList(self.difficulties.iteritems()):
                        race.addTask("TaskMovie2CheckBox", Movie2CheckBox=checkbox, Value=True)
                        race.addFunction(self.setCurrentDifficulty, checkbox, difficultyId)
                        race.addFunction(self.setScrollbarsTexts)

                with until.addIfTask(lambda: ok2Exists) as (true, false):
                    with false.addRaceTask(3) as (cancel, ok, click_out):
                        click_out.addScope(self.cancelScopeClickOut)
                        cancel.addScope(self.cancelScope)
                        ok.addScope(self.okScope, 'Movie2Button_OK')

                    with true.addRaceTask(4) as (cancel, ok, ok2, click_out):
                        click_out.addScope(self.cancelScopeClickOut)
                        cancel.addScope(self.cancelScope)
                        ok.addScope(self.okScope, 'Movie2Button_OK')
                        ok2.addScope(self.okScope, 'Movie2Button_OK2')

                until.addScope(self.scopeClose)

            #

            for CheckBox in self.difficulties.values():
                tc.addTask("TaskCheckBoxBlockState", CheckBox=CheckBox, Value=True)

            tc.addTask("TaskInteractive", ObjectName="Socket_Block", Value=False)
            tc.addTask("TaskNotify", ID=Notificator.onSelectedDifficulty)
            tc.addTask('TaskSceneLayerGroupEnable', LayerName='Difficulty', Value=False)

    def cancelScope(self, source):
        source.addTask('TaskMovie2ButtonClick', GroupName='Difficulty', Movie2ButtonName='Movie2Button_Cancel')

    def cancelScopeClickOut(self, source):
        source.addTask('TaskMovie2SocketClick', GroupName='Difficulty', Movie2Name='Movie2_Slots', SocketName='close')

    def okScope(self, source, okButtonName):
        source.addTask('TaskMovie2ButtonClick', GroupName='Difficulty', Movie2ButtonName=okButtonName)
        source.addTask("TaskFunction", Fn=self.__handleMengineSettings)

    def _onDeactivate(self):
        super(Difficulty2, self)._onDeactivate()

        if TaskManager.existTaskChain("Menu_Difficulty") is True:
            TaskManager.cancelTaskChain("Menu_Difficulty")

        for difficultyScrollbarDict in self.difficultiesScrollbars.values():
            for scrollbarData in difficultyScrollbarDict.values():
                scrollbar_obj = scrollbarData.getScrollbarObject()
                scrollbar_obj.onScrollEnd.removeObservers()