from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.MapManager import MapManager
from HOPA.StageManager import StageManager

class Map(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "VisitScenes")
        Type.addAction(Type, "Teleport")
        Type.addAction(Type, "MarkedDone")
        Type.addAction(Type, "OpenPages")
        Type.addActionActivate(Type, "CurrentID", Update=Map._updateCurrentID)
        pass

    def __init__(self):
        super(Map, self).__init__()
        self.Socket_Back = None

        self.activeTeleports = []
        self.nodeList = []
        self.layer = None
        self.Button_Left = None
        self.Button_Right = None
        pass

    def __changePage(self, num):
        for key, value in self.OpenPages.items():
            if value == self.CurrentID:
                indexCurrentPage = key
                pass
            pass
        indexNewPage = indexCurrentPage + num
        newPageID = self.OpenPages[indexNewPage]
        self.deactivatePage()
        self.object.setCurrentID(newPageID)
        self.activatePage()
        pass

    def __updateButtons(self):
        if len(self.OpenPages) < 2:
            return False
            pass

        for key, value in self.OpenPages.items():
            if value == self.CurrentID:
                indexCurrentPage = key
                pass

        if indexCurrentPage >= len(self.OpenPages) and self.Button_Left is not None:
            self.Button_Left.setParam("Interactive", 1)
            pass
        elif self.Button_Left is not None:
            self.Button_Left.setParam("Interactive", 0)
            pass

        if len(self.OpenPages) > indexCurrentPage and self.Button_Right is not None:
            self.Button_Right.setParam("Interactive", 1)
            pass
        elif self.Button_Right is not None:
            self.Button_Right.setParam("Interactive", 0)
            pass
        pass

    def _onDeactivate(self):
        self.deactivatePage()
        pass

    def _onActivate(self):
        self.activatePage()
        pass

    def __transition(self, sceneName):
        if self.Teleport is True:
            TaskManager.runAlias("AliasTransition", None, SceneName=sceneName)
            pass
        pass

    def deactivatePage(self):
        self.Socket_Back.setInteractive(False)
        self.Socket_Back = None
        self.activeTeleports = []

        for node in self.nodeList:
            Mengine.destroyNode(node)
            pass
        self.nodeList = []

        if TaskManager.existTaskChain("OpenMap"):
            TaskManager.cancelTaskChain("OpenMap")
            pass
        if TaskManager.existTaskChain("PlayMap"):
            TaskManager.cancelTaskChain("PlayMap")
            pass
        if TaskManager.existTaskChain("EnterButtons"):
            TaskManager.cancelTaskChain("EnterButtons")
            pass
        if TaskManager.existTaskChain("MapPagesLeft"):
            TaskManager.cancelTaskChain("MapPagesLeft")
            pass
        if TaskManager.existTaskChain("MapPagesRight"):
            TaskManager.cancelTaskChain("MapPagesRight")
            pass

        if self.layer is None:
            return

        self.layer.onDisable()
        pass

    def activatePage(self):
        curStage = StageManager.getCurrentStage()
        if curStage.getTag() is not "FX":
            return

        if self.object.hasObject("Button_Left"):
            self.Button_Left = self.object.getObject("Button_Left")
            self.Button_Right = self.object.getObject("Button_Right")

            with TaskManager.createTaskChain(Name="MapPagesLeft", Repeat=True) as tc:
                tc.addTask("TaskButtonClick", Button=self.Button_Left, AutoEnable=False)
                tc.addTask("TaskFunction", Fn=self.__changePage, Args=(-1,))
                pass

            with TaskManager.createTaskChain(Name="MapPagesRight", Repeat=True) as tc:
                tc.addTask("TaskButtonClick", Button=self.Button_Right, AutoEnable=False)
                tc.addTask("TaskFunction", Fn=self.__changePage, Args=(1,))
                pass
            pass

        self.MacroTypeFilter = MapManager.getMacroTypeFilter()

        tepeportsScenes = {}
        self.Socket_Back = self.object.getObject("Socket_Back")
        self.Socket_Back.setInteractive(True)

        Sprite_PlayerPlace = self.object.getObject("Sprite_PlayerPlace")
        Sprite_PlayerPlace.setEnable(False)
        Sprite_Objectives = self.object.getObject("Sprite_Objectives")
        Sprite_Objectives.setEnable(False)
        Sprite_Undiscovered = self.object.getObject("Sprite_Undiscovered")
        Sprite_Undiscovered.setEnable(False)
        Sprite_AllDone = self.object.getObject("Sprite_AllDone")
        Sprite_AllDone.setEnable(False)

        currentSceneName = SceneManager.getCurrentGameSceneName()
        teleports = MapManager.getChapterTeleports(self.CurrentID)
        for teleport in teleports:
            tepeportsScenes[teleport.clickObject] = teleport.sceneName
            pass

        ObjectivesSpriteResourceName = Sprite_Objectives.getParam("SpriteResourceName")
        PlayerPlaceSpriteResourceName = Sprite_PlayerPlace.getParam("SpriteResourceName")
        AllDoneSpriteResourceName = Sprite_AllDone.getParam("SpriteResourceName")

        currentButton = None

        for teleport in teleports:
            clickObject = teleport.getClickObject()
            if clickObject.getType() == "ObjectMovieButton":
                clickObject.setOver(False)
                pass
            clickObject.setEnable(True)
            clickObject.setParam("Interactive", 1)
            clickObjectEntity = clickObject.getEntity()
            hotspot = clickObject.getEntity().getHotSpot()

            if currentSceneName == teleport.sceneName:
                NodeSprite = Mengine.createSprite("map_player_place", PlayerPlaceSpriteResourceName)
                NodeSprite.disable()
                currentSpriteEntity = Sprite_PlayerPlace.getEntity()
                currentButton = clickObject
                if currentButton.getType() == "ObjectMovieButton":
                    currentButton.setOver(True)
                    pass
                currentButton.setParam("Interactive", 0)
                pass
            elif teleport.sceneName in self.MarkedDone:
                NodeSprite = Mengine.createSprite("map_all_done", AllDoneSpriteResourceName)
                NodeSprite.disable()
                currentSpriteEntity = Sprite_AllDone.getEntity()
                pass
            elif teleport.sceneName in self.VisitScenes:
                self.activeTeleports.append(clickObject)
                NodeSprite = Mengine.createSprite("map_objectives", ObjectivesSpriteResourceName)
                NodeSprite.disable()
                currentSpriteEntity = Sprite_Objectives.getEntity()
                pass
            elif teleport.sceneName not in self.VisitScenes:
                clickObject.setEnable(False)
                continue
                pass
            else:
                continue
                pass

            self.nodeList.append(NodeSprite)

            Position = hotspot.getWorldPolygonCenter()
            Sprite = currentSpriteEntity.getSprite()
            Origin = Sprite.getLocalImageCenter()

            clickObjectEntity.addChild(NodeSprite)
            NodeSprite.setWorldPosition((Position.x - Origin.x, Position.y - Origin.y))

            NodeSprite.enable()
            clickObject.setParam("Interactive", 0)
            pass

        lenActiveTeleports = len(self.activeTeleports)

        with TaskManager.createTaskChain(Name="PlayMap", Group=self.object) as tc:
            with tc.addRaceTask(lenActiveTeleports) as tcs:
                for tci, clickObject in zip(tcs, self.activeTeleports):
                    sceneName = tepeportsScenes[clickObject]

                    tci.addTask("TaskButtonClick", Button=clickObject)
                    tci.addTask("TaskFunction", Fn=self.__transition, Args=(sceneName,))
                    pass
                pass
            pass

        def __checkButton(button):
            if button not in self.activeTeleports:
                return False
                pass
            if button.getType() != "ObjectMovieButton":
                return False
                pass
            if currentButton is not None:
                currentButton.setOver(False)
                currentButton.setParam("Interactive", 1)
                currentButton.setParam("Interactive", 0)
                pass
            return True
            pass

        def __checkButton2(button):
            if button not in self.activeTeleports:
                return False
                pass
            if button.getType() != "ObjectMovieButton":
                return False
                pass
            if currentButton is not None:
                currentButton.setParam("Interactive", 1)
                currentButton.setOver(True)
                currentButton.setParam("Interactive", 0)
                pass
            return True
            pass

        with TaskManager.createTaskChain(Name="EnterButtons", Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskListener", ID=Notificator.onButtonMouseEnter, Filter=__checkButton)
            tc.addTask("TaskListener", ID=Notificator.onButtonMouseLeave, Filter=__checkButton2)
            pass

        pass

    def _updateCurrentID(self, value):
        if value is None:
            return

        if self.layer != value and self.layer is not None:
            self.layer.onDisable()
            pass

        CurrentSceneName = SceneManager.getCurrentSceneName()
        self.layer = SceneManager.getSceneLayerGroup(CurrentSceneName, value)
        if self.layer.isActive() is False:
            return

        self.layer.onEnable()
        self.__updateButtons()
        pass

    pass