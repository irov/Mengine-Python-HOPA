from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from HOPA.ItemManager import ItemManager
from HOPA.ScenarioChapter import ScenarioChapter
from HOPA.ScenarioManager import ScenarioManager
from HOPA.StageManager import StageManager
from HOPA.TransitionManager import TransitionManager
from Notification import Notification

from SystemDebugMenu import SystemDebugMenu


class DebugMenu(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "Font")
        Type.addAction(Type, "Zoom")
        pass

    def __init__(self):
        super(DebugMenu, self).__init__()
        self.itemButtons = {}
        self.sceneButtons = {}
        self.paragraphButtons = {}
        self.stageButtons = {}
        self.buttonPos = (50, 25)
        self.ButtonObserver = None
        self.NextButton = None
        self.LastButton = None
        self.ItemButton = None
        self.SceneButton = None
        self.StageButton = None
        self.ParagraphButton = None
        self.Inventory = None
        self.generatedNodes = {}
        self.Page = 0
        self.PreviosButtonSetup = self.setupSceneButtons
        pass

    def _onPreparation(self):
        super(DebugMenu, self)._onPreparation()
        self.Inventory = DemonManager.getDemon("Inventory")

        self.NextButton = self.object.getObject("Button_NextPage")
        self.NextButton.setInteractive(True)
        self.NextButton.setFont("__CONSOLE_FONT__")
        self.NextButton.setTextID("ID_DebugMenuNextPage")

        self.LastButton = self.object.getObject("Button_BackPage")
        self.LastButton.setInteractive(True)
        self.LastButton.setFont("__CONSOLE_FONT__")
        self.LastButton.setTextID("ID_DebugMenuBackPage")

        self.ParagraphButton = self.object.getObject("Button_ParagraphMenu")
        self.ParagraphButton.setInteractive(True)
        self.ParagraphButton.setTextID("ID_DebugMenuParagraphs")
        self.ParagraphButton.setFont("__CONSOLE_FONT__")

        self.ItemButton = self.object.getObject("Button_ItemMenu")
        self.ItemButton.setInteractive(True)
        self.ItemButton.setFont("__CONSOLE_FONT__")
        self.ItemButton.setTextID("ID_DebugMenuItems")

        self.SceneButton = self.object.getObject("Button_SceneMenu")
        self.SceneButton.setInteractive(True)
        self.SceneButton.setFont("__CONSOLE_FONT__")
        self.SceneButton.setTextID("ID_DebugMenuScenes")

        if self.object.hasObject("Button_StageMenu") is True:
            self.StageButton = self.object.getObject("Button_StageMenu")
            self.StageButton.setInteractive(True)
            self.StageButton.setFont("__CONSOLE_FONT__")
            self.StageButton.setTextID("ID_DebugMenuStages")
            pass

        self.setupSceneButtons()
        pass

    def setupSceneButtons(self):
        self.destroyButtons()

        self.ItemButton.setEnable(True)
        self.ParagraphButton.setEnable(True)
        self.SceneButton.setEnable(False)
        if self.StageButton is not None:
            self.StageButton.setEnable(True)
            pass

        sceneNameArray = sorted(SceneManager.getScenes())

        y = -30
        x = -250

        resolutionY = Mengine.getContentResolution().getHeight()
        resolutionOffset = resolutionY * 0.2
        Buttons_per_page = 40

        for i in range(len(sceneNameArray)):
            iterator = i + Buttons_per_page * self.Page
            if i + 1 > Buttons_per_page or iterator > (len(sceneNameArray) - 1):
                return

            sceneName = sceneNameArray[iterator]

            # for sceneName in curChapterGameScenes:

            ###### Button differentiation feature
            ScenarioID = ScenarioManager.getScenarioIdBySceneName(sceneName)
            if ScenarioID is None:
                Scene_is_ItemPlus = False
            else:
                ScenarioDesc = ScenarioManager.getScenario(ScenarioID)
                Scene_is_ItemPlus = ScenarioDesc.PlusName

            # Scene_is_HOG_or_Puzzle = len(EnigmaManager.getSceneEnigmas(sceneName)) != 0

            BaseScene = SceneManager.getSceneBase(sceneName)

            MGStr = "MG"
            HOGStr = "HOG"
            PuzzleStr = "Puzzle"
            PlusStr = "Plus"

            Scene_is_MG = MGStr in sceneName
            Scene_is_HOG_or_Puzzle = HOGStr == BaseScene[:len(HOGStr)] or PuzzleStr == BaseScene[:len(PuzzleStr)]
            Scene_is_ItemPlus = PlusStr in sceneName
            Scene_is_CutScene = BaseScene == "CutScene"

            button = self.object.generateObject("Button_%s" % (sceneName), "Button_Scene")
            if Scene_is_MG is True:
                button.setParam("RGB", (1.0, 0.0, 0.0, 1.0))
            elif Scene_is_ItemPlus is True:
                button.setParam("RGB", (1.0, 1.0, 0.0, 1.0))
            elif Scene_is_HOG_or_Puzzle is True:
                button.setParam("RGB", (0.0, 1.0, 0.0, 1.0))
            elif Scene_is_CutScene is True:
                button.setParam("RGB", (1.0, 0.5, 0.0, 1.0))
            else:
                button.setParam("RGB", (1.0, 1.0, 1.0, 1.0))
            ######

            button.setFont("__CONSOLE_FONT__")
            button.setTextID("ID_DebugMenuScene")

            button.setTextArgs(sceneName)

            button.setFontRGBA((0, 0, 0, 1))
            button.setPosition((self.buttonPos[0] + x, self.buttonPos[1] + y))
            button.setEnable(True)
            button.setInteractive(True)
            if self.Font is not None:
                button.setFont(self.Font)
                pass
            y += 65  # 50
            if y >= (resolutionY - resolutionOffset):
                y = 0
                x += 228 * 1.4
                pass
            self.sceneButtons[button] = sceneName
            pass
        pass

    def setupParagraphButtons(self):
        self.destroyButtons()
        self.ItemButton.setEnable(True)
        self.ParagraphButton.setEnable(False)
        self.SceneButton.setEnable(True)
        if self.StageButton is not None:
            self.StageButton.setEnable(True)
            pass
        SceneName = SceneManager.getPrevSceneName()
        GroupName = self.Zoom
        if GroupName is None:
            GroupName = SceneManager.getSceneMainGroupName(SceneName)
            pass
        # GroupName = SceneManager.getSceneMainGroupName(SceneName)

        curStage = StageManager.getCurrentStage()
        if curStage.getTag() is not "FX":
            return False
            pass

        Scenario = curStage.getScenarioChapter()
        curScenarios = ScenarioChapter.findSceneScenarios(Scenario, SceneName)

        scenarioParagraphs = []
        for sc in curScenarios:
            if sc.GroupName == GroupName:
                scenario = sc
                scenarioParagraphs.append(scenario.Scenario.getWaitParagraphs())
                pass
            pass

        values = []
        for waitParagraphs in scenarioParagraphs:
            for pr in waitParagraphs:
                for id in pr.Paragraphs:
                    if id in values:
                        continue
                        pass
                    values.append(id)
                    pass
                pass
            pass

        y = -30
        x = -150
        resolutionY = Mengine.getContentResolution().getHeight()
        resolutionOffset = resolutionY * 0.2

        for id in values:
            button = self.object.generateObject("Button_%s" % (id), "Button_Scene")
            button.setFont("__CONSOLE_FONT__")
            button.setTextID("ID_DebugMenuScene")
            button.setTextArgs(id)
            button.setFontRGBA((0, 0, 0, 1))
            button.setPosition((self.buttonPos[0] + x, self.buttonPos[1] + y))
            button.setEnable(True)
            button.setInteractive(True)
            if self.Font is not None:
                button.setFont(self.Font)
                pass
            y += 45  # 50
            if y >= (resolutionY - resolutionOffset):
                y = 0
                x += 330  # 460 #228
                pass
            self.paragraphButtons[button] = id
            pass
        pass

    def setupItemButtons(self):
        self.destroyButtons()
        self.ItemButton.setEnable(False)
        self.ParagraphButton.setEnable(True)
        self.SceneButton.setEnable(True)
        if self.StageButton is not None:
            self.StageButton.setEnable(True)
            pass

        itemNameArray = []
        items = ItemManager.getAllItems()
        y = -30
        x = -250
        resolutionY = Mengine.getContentResolution().getHeight()
        resolutionOffset = resolutionY * 0.2

        Buttons_per_page = 40

        for itemName in items:
            itemNameArray.append(itemName)

        def items_sort(item_name):
            splitted_name = item_name.split("_")
            return int(splitted_name[-1])

        itemNameArray.sort(key=items_sort)

        for i in range(len(itemNameArray)):
            iterator = i + Buttons_per_page * self.Page
            if i > Buttons_per_page or iterator > (len(itemNameArray) - 1):
                return
            itemName = itemNameArray[iterator]

            # for itemName in items:
            InventoryItem = ItemManager.getItemInventoryItem(itemName)
            if self.Inventory.hasInventoryItem(InventoryItem) is True:
                continue
                pass

            def __generateSpriteCopy(InventoryItem, position):
                name = InventoryItem.getName()
                SpriteResourceName = InventoryItem.getSpriteResourceName()

                if SpriteResourceName is None:
                    return None

                node = Mengine.createSprite(name, SpriteResourceName)
                node.setLocalPosition(position)

                return node
                pass

            button = self.object.generateObject("Button_%s" % (itemName), "Button_Scene")
            button.setFont("__CONSOLE_FONT__")
            button.setTextID("ID_DebugMenuItem")
            button.setTextArgs(itemName)
            button.setFontRGBA((0, 0, 0, 1))
            button.setPosition((self.buttonPos[0] + x, self.buttonPos[1] + y))
            button.setEnable(True)
            button.setInteractive(True)
            node = __generateSpriteCopy(InventoryItem, (self.buttonPos[0] + x + 200, self.buttonPos[1] + y))  # -15 +15

            if node is not None:
                self.addChild(node)
            if self.Font is not None:
                button.setFont(self.Font)
                pass
            y += 90  # 75
            if y >= (resolutionY - resolutionOffset):
                y = 0
                x += 228 * 1.4  # /2#480 #150
                pass
            self.itemButtons[button] = itemName
            self.generatedNodes[button] = node
            pass
        pass

    def setupStageButtons(self):
        self.destroyButtons()

        self.ItemButton.setEnable(True)
        self.ParagraphButton.setEnable(True)
        self.SceneButton.setEnable(True)

        self.StageButton.setEnable(False)

        stages = StageManager.getStageLabels()
        y = 0
        x = 0
        resolutionY = Mengine.getContentResolution().getHeight()
        resolutionOffset = resolutionY * 0.2

        for stage, label in stages.iteritems():
            button = self.object.generateObject("Button_%s" % (stage), "Button_Scene")
            button.setFont("__CONSOLE_FONT__")
            button.setTextID("ID_DebugMenuScene")
            button.setTextArgs(label)
            button.setFontRGBA((0, 0, 0, 1))
            button.setPosition((self.buttonPos[0] + x, self.buttonPos[1] + y))
            button.setEnable(True)
            button.setInteractive(True)
            if self.Font is not None:
                button.setFont(self.Font)
                pass
            y += 50
            if y >= (resolutionY - resolutionOffset):
                y = 0
                x += 228
                pass
            self.stageButtons[button] = stage
            pass
        pass

    def destroyButtons(self):
        for node in self.generatedNodes.values():
            if node is None:
                continue
            Mengine.destroyNode(node)
            pass

        self.generatedNodes = {}

        for button in self.sceneButtons:
            button.onDestroy()
            pass
        self.sceneButtons = {}

        for button in self.itemButtons:
            button.onDestroy()
            pass

        self.itemButtons = {}

        for button in self.paragraphButtons:
            button.onDestroy()
            pass

        self.paragraphButtons = {}

        for button in self.stageButtons:
            button.onDestroy()
            pass

        self.stageButtons = {}
        pass

    def addItem(self, itemName):
        self.Inventory.addItem(itemName)

        InventoryItem = ItemManager.getItemInventoryItem(itemName)
        InventoryItem.appendParam("FoundItems", itemName)
        pass

    def _onActivate(self):
        super(DebugMenu, self)._onActivate()
        self.ButtonObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        pass

    def __onButtonClick(self, button):
        if button in self.stageButtons:
            SystemDebugMenu.s_is_showable = False
            stage = self.stageButtons[button]
            StageManager.runStage(stage)
            self.setupSceneButtons()
            return False
            pass
        if button in self.sceneButtons:
            SystemDebugMenu.s_is_showable = False
            sceneName = self.sceneButtons[button]

            TransitionManager.changeScene(sceneName, fade=False)

            return False
            pass
        if button in self.itemButtons:
            itemName = self.itemButtons[button]
            del self.itemButtons[button]
            button.onDestroy()
            node = self.generatedNodes[button]
            del self.generatedNodes[button]
            if node is not None:
                node.removeFromParent()
            self.addItem(itemName)
            return False
            pass
        if button in self.paragraphButtons:
            paragraphID = self.paragraphButtons[button]
            del self.paragraphButtons[button]
            button.onDestroy()
            Notification.notify(Notificator.onParagraphRun, paragraphID)

        elif button is self.ItemButton:
            self.Page = 0
            self.setupItemButtons()
            self.PreviosButtonSetup = self.setupItemButtons

        elif button is self.SceneButton:
            self.Page = 0
            self.setupSceneButtons()
            self.PreviosButtonSetup = self.setupSceneButtons

        elif button is self.ParagraphButton:
            self.Page = 0
            self.setupParagraphButtons()

        elif button is self.StageButton:
            self.Page = 0
            self.setupStageButtons()

        elif button is self.NextButton:
            self.change_Page(1)
            self.PreviosButtonSetup()

        elif button is self.LastButton:
            self.change_Page(-1)
            self.PreviosButtonSetup()

        return False
        pass

    def change_Page(self, value):
        self.Page += value
        if self.Page < 0:
            self.Page = 0

    def _onDeactivate(self):
        super(DebugMenu, self)._onDeactivate()
        Notification.removeObserver(self.ButtonObserver)
        self.destroyButtons()
        pass

    pass
