from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager
from HOPA.QuestManager import QuestManager
from HOPA.ZoomManager import ZoomManager
from HOPA.SpellsManager import SpellsManager, SPELL_AMULET_TYPE
from HOPA.System.SystemItemPlusScene import SystemItemPlusScene


class SystemDebugShowUsageItem(System):
    QuestCheckTypes = ["UseInventoryItem", "GiveItemOr", "CompleteItemCount"]

    def __init__(self):
        super(SystemDebugShowUsageItem, self).__init__()
        self.Observers = []
        self.Handler = None
        self.InventoryItem = None
        self.Inventory = None

        self.Use = False

        self._spell_amulet_quest_type = None

    def _onRun(self):
        if SpellsManager.getSpellsUIButtonParam(SPELL_AMULET_TYPE) is not None:
            self._spell_amulet_quest_type = SpellsManager.getSpellsUIButtonParam(SPELL_AMULET_TYPE).spell_use_quest

        self.Handler = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)

        return True

    def __onGlobalHandleKeyEvent(self, event):
        if not Mengine.hasOption('cheats'):
            return

        if SceneManager.isCurrentGameScene() is False:
            return None
            pass

        if ArrowManager.emptyArrowAttach() is False:
            return None
            pass

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return None

        if event.isDown is True and event.isRepeat is False:
            key = DefaultManager.getDefaultKey("CheatsGetUsageItem", "VK_SHIFT")
            if key is None or key == Mengine.KC_SHIFT:
                if Mengine.isShiftKeyCode(event.code) is False:
                    return None
            elif event.code != key:
                return None
            self.beginDebugShow()

            return None
            pass

        return None
        pass

    def beginDebugShow(self):
        sceneName = SceneManager.getCurrentSceneName()
        zoomGroupName = ZoomManager.getZoomOpenGroupName()

        if SystemItemPlusScene.Open_Zoom is not None:
            sceneName = SystemItemPlusScene.Open_Zoom[1]
            groupName = SystemItemPlusScene.Open_Zoom[0].getName()
        elif zoomGroupName is not None:
            groupName = zoomGroupName
        else:
            groupName = SceneManager.getSceneMainGroupName(sceneName)

        quests = QuestManager.getActiveItemQuests(sceneName, groupName, SystemDebugShowUsageItem.QuestCheckTypes)

        if len(quests) == 0:
            quests = QuestManager.getSceneQuests(sceneName, groupName)
            for elem in quests:
                if elem.questType == "UseRune":
                    if elem.active:
                        self._generate_magic_glove_rune(elem)
                if self._spell_amulet_quest_type is not None:
                    if elem.questType == self._spell_amulet_quest_type:
                        self._generate_spell_amulet_rune(elem)
            return

        for quest in quests:
            self.generateDebugOverview(quest)

    def _generate_spell_amulet_rune(self, quest):
        self.Use = True

        DemonSpellAmulet = DemonManager.getDemon("SpellAmulet")
        PowerType = quest.params["PowerType"]

        with TaskManager.createTaskChain(Cb=self.__endShowUsageItem) as tc:
            amulet_button = DemonSpellAmulet.getSpellAmuletButton(PowerType)

            if amulet_button.getLocked() is True:
                tc.addNotify(Notificator.onSpellAmuletAddPower, PowerType, False, False)
                tc.addNotify(Notificator.onSpellUISpellUpdate, SPELL_AMULET_TYPE)

            tc.addScope(DemonSpellAmulet.scopeOpenAmulet)

    def _generate_magic_glove_rune(self, quest):
        self.Use = True

        DemonMagicGlove = DemonManager.getDemon('MagicGlove')
        RuneID = quest.params['Rune_ID']
        if RuneID in DemonMagicGlove.getParam("Runes"):
            return
        with TaskManager.createTaskChain(Cb=self.__endShowUsageItem) as source:
            def _give_rune():
                DemonMagicGlove.appendParam("Runes", RuneID)
                DemonMagicGlove.setParam("State", "Ready")

            source.addFunction(_give_rune)

    def __endShowUsageItem(self, isSkip):
        self.Use = False
        pass

    def generateDebugOverview(self, quest):
        if self.Use is True:
            return
            pass

        Object = quest.params.get("Object")

        if Object.isActive() is False:
            return
            pass

        objectEntity = Object.getEntity()
        objectHotspot = objectEntity.getHotSpot()
        pickerOver = objectHotspot.isMousePickerOver()

        if pickerOver is False:
            return
            pass

        self.InventoryItem = quest.params.get("InventoryItem")
        self.Inventory = quest.params.get("Inventory")

        ItemName = ItemManager.getInventoryItemKey(self.InventoryItem)
        PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling", "PolicyInventoryScrollingDefault")

        self.Use = True

        with TaskManager.createTaskChain(Cb=self.__endShowUsageItem) as source:
            # - fix for CountItem --------------------------------------------------------------
            if self.InventoryItem.getType() == "ObjectInventoryCountItem":  # dummy check for CountItem
                FindItems = ItemManager.getInventoryItemFindItems(self.InventoryItem)

                if self.InventoryItem.hasParam("PlayedItems") is True:  # dummy check for CountItemFX
                    source.addFunction(self.InventoryItem.setParam, "Combined", True)

                    for find_item in FindItems:
                        Item = ItemManager.getItem(find_item)
                        if Item.PartSubMovieName is None:
                            continue

                        source.addFunction(self.InventoryItem.appendParam, "PlayedItems", Item.PartSubMovieName)

                for find_item in FindItems:
                    source.addFunction(self.InventoryItem.appendParam, "FoundItems", find_item)
            # ----------------------------------------------------------------------------------

            source.addTask("TaskNotify", ID=Notificator.onItemClickToInventory,
                           Args=(self.Inventory, ItemName, "ActionHintUse"))
            source.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=ItemName, ItemHide=True)
            source.addTask("TaskDelay", Time=0.01 * 1000)  # speed fix
            source.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.Inventory,
                           InventoryItem=self.InventoryItem)
            source.addTask(PolicyInventoryScrolling, InventoryItem=self.InventoryItem)
            source.addTask("AliasInventoryItemAttach", InventoryItem=self.InventoryItem)
            source.addFunction(self.Inventory.UnBlockButtons)
            pass
        pass

    def _onStop(self):
        super(SystemDebugShowUsageItem, self)._onStop()

        Mengine.removeGlobalHandler(self.Handler)
        pass

    pass
