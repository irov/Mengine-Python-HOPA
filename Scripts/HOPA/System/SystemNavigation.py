from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.Object.ObjectTransition import ObjectTransition
from Foundation.Object.ObjectZoom import ObjectZoom
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from HOPA.TransitionHighlightManager import TransitionHighlightManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager

class SystemNavigation(System):
    __use_movie2buttons__ = False  # check if we using old buttons or new movie2buttons

    s_highlight = {}
    s_show_warnings = True

    def _onParams(self, params):
        super(SystemNavigation, self)._onParams(params)
        SystemNavigation.s_highlight = {"AlphaTime": DefaultManager.getDefaultFloat("MobileNavigationTransitionHighlightAlpha", 500.0), "ShowTime": DefaultManager.getDefaultFloat("MobileNavigationTransitionHighlightTime", 5000.0), "StairsDelay": DefaultManager.getDefaultFloat("MobileNavigationTransitionHighlightStairsDelay", 340.0), "ShowWarnings": DefaultManager.getDefaultBool("MobileNavigationTransitionShowWarnings", True), }
        SystemNavigation.s_show_warnings = DefaultManager.getDefaultBool("MobileNavigationTransitionShowWarnings", True)

    def _onStop(self):
        self.__destroyTransHighlightMovies()
        super(SystemNavigation, self)._onStop()

    def _onRun(self):
        super(SystemNavigation, self)._onRun()

        self.__activeTransitionHighlightCache = []

        if self.isNavigationAllowed() and self.isNavigationButtonsExists():
            self.addObserver(Notificator.onNavigationButtonPressed, self.__navHighlightPressedObserver)
            self.addObserver(Notificator.onButtonBackPressed, self.__navBackPressedObserver)
            self.addObserver(Notificator.onSceneEnter, self.__sceneEnterObserver)
            self.addObserver(Notificator.onSceneLeave, self.__sceneLeaveObserver)

            self.__createButtonClickTaskChain()

        else:
            self.__disableNavigationButtons()

        return True

    @staticmethod
    def getHighlightParam(key):
        return SystemNavigation.s_highlight.get(key)

    @staticmethod
    def isNavigationAllowed():
        return Mengine.hasTouchpad()

    @staticmethod
    def isNavigationButtonsExists():
        navDemon = GroupManager.getObject("Navigation", "Demon_Navigation")

        # CHECK NEW MOVIE 2 BUTTONS
        if navDemon.hasObject("Movie2Button_NavShowTransitions") and navDemon.hasObject("Movie2Button_NavShowTransitions"):
            SystemNavigation.__use_movie2buttons__ = True
            return True

        # CHECK DEPRECATED BUTTONS
        if navDemon.hasObject("Button_Navigation") and navDemon.hasObject("Button_Back"):
            SystemNavigation.__use_movie2buttons__ = False
            if _DEVELOPMENT is True and SystemNavigation.s_show_warnings is True:
                Trace.msg_err("[Warning] SystemNavigation: In Group_Navigation/Demon_Navigation Used Deprecated buttons: Button_Navigation, Button_Back. Please Use Movie2Button_NavShowTransitions and Movie2Button_NavGoBack")
            return True

        Trace.log("System", 0, "[Error] SystemNavigation: In Group_Navigation/Demon_Navigation not found Movie2Button_NavShowTransitions or Movie2Button_NavGoBack. Make sure both exists")

        return False

    @staticmethod
    def getNavTransitionButton():
        navDemon = GroupManager.getObject("Navigation", "Demon_Navigation")

        if navDemon.hasObject("Movie2Button_NavShowTransitions"):
            return navDemon.getObject("Movie2Button_NavShowTransitions")

        if navDemon.hasObject("Button_Navigation"):
            return navDemon.getObject("Button_Navigation")

    @staticmethod
    def getNavGoBackButton():
        navDemon = GroupManager.getObject("Navigation", "Demon_Navigation")

        if navDemon.hasObject("Movie2Button_NavGoBack"):
            return navDemon.getObject("Movie2Button_NavGoBack")

        if navDemon.hasObject("Button_Back"):
            return navDemon.getObject("Button_Back")

    def __disableNavigationButtons(self):
        navDemon = GroupManager.getObject("Navigation", "Demon_Navigation")

        # HANDLE DEPRECATED BUTTONS
        if navDemon.hasObject("Button_Navigation"):
            navigation_button = navDemon.getObject("Button_Navigation")
            navigation_button.setEnable(False)

        if navDemon.hasObject("Button_Back"):
            button_back = navDemon.getObject("Button_Back")
            button_back.setEnable(False)

        # HANDLE NEW MOVIE 2 BUTTONS
        if navDemon.hasObject("Movie2Button_NavShowTransitions"):
            navigation_button = navDemon.getObject("Movie2Button_NavShowTransitions")
            navigation_button.setEnable(False)

        if navDemon.hasObject("Movie2Button_NavGoBack"):
            button_back = navDemon.getObject("Movie2Button_NavGoBack")
            button_back.setEnable(False)

    @staticmethod
    def getScenesAndZoomsTransitionsToHighlight():
        toHighlightScenes = []
        toHighlightZooms = []

        if SceneManager.isCurrentGameScene():
            currentScene = SceneManager.getCurrentGameSceneName()

            # get transition Objects lists to highlight:
            toHighlightScenes = TransitionManager.getActiveSceneTransitionObjects(currentScene)
            toHighlightZooms = ZoomManager.getActiveSceneZoomObjects(currentScene)

            # filter out currently highlighted in SystemTransitionHighlight
            if SystemManager.hasSystem("SystemTransitionHighlight"):
                sysTransHighlight = SystemManager.getSystem("SystemTransitionHighlight")

                toHighlightScenes = [scene for scene in toHighlightScenes if not sysTransHighlight.IsObjectHighlightedNow(scene)]
                toHighlightZooms = [zoom for zoom in toHighlightZooms if not sysTransHighlight.IsObjectHighlightedNow(zoom)]

        return toHighlightScenes, toHighlightZooms

    @staticmethod
    def hasTransitionsToHighlight():
        """
        :return: True if eny zoom or scene transition exists and it can be highlighted
        """
        scenesToLit, zoomsToLit = SystemNavigation.getScenesAndZoomsTransitionsToHighlight()
        return len(scenesToLit) > 0 or len(zoomsToLit) > 0

    def __createMovie_TransitionHighlightFX(self, objToLit):
        """
        objToLit: can be zoomObject or transitionObject

        finds proper highlight movie prototype in TransitionHighlight group,
        if not found, will be used default movie (exactly one which used in HO highlight)

        :return: created ObjectMovie2 instance
        """

        scene = SceneManager.getCurrentScene()
        if scene is None:
            return
        layer = scene.getMainLayer()
        group = GroupManager.getGroup("TransitionHighlight")
        movieSpawnParam = {"Enable": True, "Play": True, "Loop": True, "Alpha": 0.0}

        # get prototype name:
        if isinstance(objToLit, ObjectZoom):
            if group.hasPrototype("Movie2_MobileNavHighlightZooms"):
                prototypeName = "Movie2_MobileNavHighlightZooms"
            else:
                transLitParam = TransitionHighlightManager.s_transitionHighlights.itervalues().next()  # get first transition highlight effect prototype
                prototypeName = transLitParam.prototypeName
                if _DEVELOPMENT is True and SystemNavigation.s_show_warnings is True:
                    Trace.msg_err("GroupNavigation not found Movie2_MobileNavHighlightZooms prototype. Used movie for HO Highlight: '%s'" % prototypeName)
        elif isinstance(objToLit, ObjectTransition):
            if group.hasPrototype("Movie2_MobileNavHighlightScenes"):
                prototypeName = "Movie2_MobileNavHighlightScenes"
            else:
                transLitParam = TransitionHighlightManager.s_transitionHighlights.itervalues().next()  # get first transition highlight effect prototype
                prototypeName = transLitParam.prototypeName
                if _DEVELOPMENT is True and SystemNavigation.s_show_warnings is True:
                    Trace.msg_err("GroupNavigation not found Movie2_MobileNavHighlightScenes prototype. Used movie for HO Highlight: '%s'" % prototypeName)
        else:
            Trace.log("System", 0, "Wrong type: {}!!! SystemNavigation.__createMovie_TransitionHighlightFX() supports only type ObjectZoom and ObjectTransition.".format(objToLit.__class__.__name__))
            return

        # spawn movie:
        spawnedMovie = group.generateObject("%s_%s" % (prototypeName, objToLit.getName()), prototypeName, movieSpawnParam)
        if spawnedMovie:
            # set position:
            node = spawnedMovie.getEntityNode()
            node.removeFromParent()
            layer.addChild(node)
            if node:
                node.setLocalPosition(objToLit.calcWorldHintPoint())

            self.__activeTransitionHighlightCache.append(spawnedMovie)

        return spawnedMovie

    def __navHighlightPressedObserver(self):
        """
        main method for handling logic on transition highlight button clicked

        this method will create temp movies to highlight transitions from scenes to zooms and other scenes
        """

        scenesToLitTransitions, zoomsToLitTransitions = self.getScenesAndZoomsTransitionsToHighlight()

        if self.existTaskChain("HighlightFX"):
            self.removeTaskChain("HighlightFX")
        self.__destroyTransHighlightMovies()

        for transitionObj in scenesToLitTransitions:
            self.__createMovie_TransitionHighlightFX(transitionObj)

        for zoomObj in zoomsToLitTransitions:
            self.__createMovie_TransitionHighlightFX(zoomObj)

        with self.createTaskChain(Name="HighlightFX", Global=False, Repeat=False) as tc:
            alpha_time = self.getHighlightParam("AlphaTime")
            show_time = self.getHighlightParam("ShowTime")
            stairsDelay = 0.0  # timer for appearing each highlight after some delay

            for litMovie, source in tc.addParallelTaskList(self.__activeTransitionHighlightCache):
                # stairs delay effect
                source.addDelay(stairsDelay)
                source.addTask("AliasObjectAlphaTo", Object=litMovie, Time=alpha_time, From=0.0, To=1.0, Easing="easyIn")
                source.addDelay(show_time)
                source.addTask("AliasObjectAlphaTo", Object=litMovie, Time=alpha_time, From=1.0, To=0.0, Easing="easyOut")

                stairsDelay += self.getHighlightParam("StairsDelay")  # stairs delay accumulation

            tc.addFunction(self.__destroyTransHighlightMovies)

        return False

    def __navBackPressedObserver(self):
        """
        main method for handling logic on button back clicked

        making transition to previous scene is it's possible
        """
        currentSceneName = SceneManager.getCurrentGameSceneName()
        prevSceneName = TransitionManager.getTransitionBack(currentSceneName)
        if prevSceneName:
            TransitionManager.changeScene(prevSceneName)

        return False

    def __createButtonClickTaskChain(self):
        with self.createTaskChain(Name="Navigation_ButtonClick", Global=False, Repeat=True) as tc:
            with tc.addRaceTask(2) as (race_0, race_1):
                if self.__use_movie2buttons__:
                    # HANDLE NEW MOVIE 2 BUTTONS
                    race_0.addTask("TaskMovie2ButtonClick", Movie2Button=self.getNavTransitionButton())
                    race_0.addNotify(Notificator.onNavigationButtonPressed)

                    race_1.addTask("TaskMovie2ButtonClick", Movie2Button=self.getNavGoBackButton())
                    race_1.addNotify(Notificator.onButtonBackPressed)
                else:
                    # HANDLE DEPRECATED BUTTONS
                    race_0.addTask("TaskButtonClick", Button=self.getNavTransitionButton())
                    race_0.addNotify(Notificator.onNavigationButtonPressed)

                    race_1.addTask("TaskButtonClick", Button=self.getNavGoBackButton())
                    race_1.addNotify(Notificator.onButtonBackPressed)

    def __handleBlockStateGoBackButton(self, sceneName):
        """
        set block state on movie2button if there are no transitions we can highlight
        """
        if self.__use_movie2buttons__:
            highlightTransButton = self.getNavTransitionButton()
            if highlightTransButton:
                highlightTransButton.setBlock(not self.hasTransitionsToHighlight())

    def __handleBlockStateTransitionButton(self, sceneName):
        """
        set block state on movie2button if no transition back exists
        """
        if self.__use_movie2buttons__:
            goBackButton = self.getNavGoBackButton()
            if goBackButton:
                hasTransitionBack = TransitionManager.getTransitionBack(sceneName)
                goBackButton.setBlock(not hasTransitionBack)

    def __sceneEnterObserver(self, sceneName):
        self.__handleBlockStateTransitionButton(sceneName)
        self.__handleBlockStateGoBackButton(sceneName)
        return False

    def __destroyTransHighlightMovies(self):
        for movie in self.__activeTransitionHighlightCache:
            movie.removeFromParent()
            movie.onDestroy()
        self.__activeTransitionHighlightCache = []

    def __sceneLeaveObserver(self, sceneName):
        currentScene = SceneManager.getCurrentSceneName()
        self.__handleBlockStateTransitionButton(currentScene)

        if self.existTaskChain("HighlightFX"):
            self.removeTaskChain("HighlightFX")

        self.__destroyTransHighlightMovies()

        return False