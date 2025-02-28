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
from HOPA.ElementalMagicManager import QUEST_USE_MAGIC_NAME as ELEMENTAL_MAGIC_QUEST_USE_NAME


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

        if Mengine.hasTouchpad() is True:
            self._addMobileHandler()
        else:
            self.Handler = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)

        return True

    def _addMobileHandler(self):
        if TaskManager.existTaskChain("SystemDebugShowUsageItem") is True:
            TaskManager.cancelTaskChain("SystemDebugShowUsageItem")

        event_click_ok = Event("onClickSuccess")
        delay = DefaultManager.getDefaultFloat("CheatsGetUsageItemMobileClickDelaySeconds", 1) * 1000.0
        click_count = DefaultManager.getDefaultInt("CheatsGetUsageItemMobileClickCount", 5)

        with TaskManager.createTaskChain(Name="SystemDebugShowUsageItem", Repeat=True) as tc:
            with tc.addRepeatTask() as (repeat, until):
                with repeat.addRaceTask(2) as (race1, race2):
                    for i in range(click_count):
                        race1.addTask("TaskMouseButtonClick")
                    race1.addFunction(event_click_ok)

                    race2.addTask("TaskMouseButtonClick")   # anti stack cycle fix
                    race2.addDelay(delay)
                until.addEvent(event_click_ok)

            tc.addFunction(self.beginDebugShow)

    def __onGlobalHandleKeyEvent(self, event):
        if not Mengine.hasOption('cheats'):
            return None

        if SceneManager.isCurrentGameScene() is False:
            return None

        if ArrowManager.emptyArrowAttach() is False:
            return None

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

        return None

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
            all_quests = QuestManager.getSceneQuests(sceneName, groupName)
            for quest in all_quests:
                self.generateOtherDebugOverview(quest)
            return

        for quest in quests:
            self.generateItemDebugOverview(quest)

    def _generate_spell_amulet_rune(self, quest):
        self.Use = True

        DemonSpellAmulet = DemonManager.getDemon("SpellAmulet")
        PowerType = quest.params["PowerType"]

        with TaskManager.createTaskChain(Cb=self.__endShowUsageItem) as tc:
            amulet_button = DemonSpellAmulet.getSpellAmuletButton(PowerType)

            tc.addScope(DemonSpellAmulet.scopeOpenAmulet)

            if amulet_button.getLocked() is True:
                tc.addNotify(Notificator.onSpellAmuletAddPower, PowerType, False, False)

            tc.addNotify(Notificator.onSpellUISpellUpdate, SPELL_AMULET_TYPE, updateStatePlay=False)

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

    def _generate_elemental_magic_elem(self, quest):
        self.Use = True

        magic_id = quest.params["MagicId"]
        element = quest.params["Element"]

        Notification.notify(Notificator.onElementalMagicPick, element, magic_id)

        self.Use = False

    def __endShowUsageItem(self, isSkip):
        self.Use = False
        pass

    def generateItemDebugOverview(self, quest):
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

            source.addNotify(Notificator.onItemClickToInventory, self.Inventory, ItemName, "ActionHintUse")
            source.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=ItemName, ItemHide=True)
            source.addDelay(0.01 * 1000)  # speed fix
            source.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.Inventory,
                           InventoryItem=self.InventoryItem)
            source.addTask(PolicyInventoryScrolling, InventoryItem=self.InventoryItem)
            source.addTask("AliasInventoryItemAttach", InventoryItem=self.InventoryItem)
            source.addFunction(self.Inventory.UnBlockButtons)

    def generateOtherDebugOverview(self, quest):
        if quest.active is False:
            return

        quest_type = quest.questType

        if quest_type == "UseRune":
            self._generate_magic_glove_rune(quest)

        if self._spell_amulet_quest_type is not None and quest_type == self._spell_amulet_quest_type:
            self._generate_spell_amulet_rune(quest)

        if quest_type == ELEMENTAL_MAGIC_QUEST_USE_NAME:
            self._generate_elemental_magic_elem(quest)

    def _onStop(self):
        super(SystemDebugShowUsageItem, self)._onStop()

        if self.Handler is not None:
            Mengine.removeGlobalHandler(self.Handler)
            self.Handler = None

        if TaskManager.existTaskChain("SystemDebugShowUsageItem") is True:
            TaskManager.cancelTaskChain("SystemDebugShowUsageItem")
