from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroItemAction(MacroCommand):
    def _onValues(self, values):
        self.SocketName = values[0]
        self.ItemName = values[1]
        self.Taken = bool(values[2])  # input 0/1
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found in InventoryItems.xlsx" % (self.ItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))
                pass

            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("MacroGiveItem not found Object %s in group %s" % (self.SocketName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        FinderType, Object = self.findObject(self.SocketName)

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        Inventory = DemonManager.getDemon("Inventory")

        ObjectName = Object.getName()
        ObjectType = Object.getType()

        fan_group = GroupManager.getGroup("Fan")
        Movie_Open = fan_group.getObject("Movie_Open")

        pos = Object.getPolygon()
        Movie_Open.setPosition(pos[0])

        Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, Inventory=Inventory,
                              GroupName=self.GroupName, InventoryItem=InventoryItem, Object=Object)

        with Quest as tc_quest:
            if ObjectType == "ObjectSocket":
                tc_quest.addTask("TaskSocketPlaceInventoryItem", SocketName=ObjectName, InventoryItem=InventoryItem,
                                 ItemName=self.ItemName, Taken=self.Taken, Pick=False)
                tc_quest.addTask("TaskSceneLayerGroupEnable", LayerName="Fan", Value=True)
                tc_quest.addTask("TaskFunction", Fn=self._AttendMovieSlots, Args=("Movie_Open",))
                tc_quest.addTask("TaskMoviePlay", Movie=Movie_Open, Wait=False, LastFrame=None, Reverse=False)

            elif ObjectType == "ObjectItem":
                tc_quest.addTask("TaskItemPlaceInventoryItem", ItemName=ObjectName, InventoryItem=InventoryItem,
                                 Taken=self.Taken, Pick=False)

            elif ObjectType == "ObjectTransition" and self.Taken:
                tc_quest.addTask("TaskTransitionGiveInventoryItem", TransitionName=ObjectName,
                                 InventoryItem=InventoryItem)

            elif ObjectType == "ObjectZoom" and self.Taken:
                tc_quest.addTask("TaskZoomGiveInventoryItem", ZoomName=ObjectName, InventoryItem=InventoryItem)

        source.addListener(Notificator.onInventoryUpdateItem)

    def _AttendMovieSlots(self, MovieName):
        fan_group = GroupManager.getGroup("Fan")
        #        FindItems = self.object.getFindItems()
        #        FoundItems = self.object.getFoundItems()
        countFindItems = 3

        Movie_Open = fan_group.getObject(MovieName)
        Movie_Open_Entity = Movie_Open.getEntity()

        #        ObjList = [FanItemManager.getItemObject(item) for item in FindItems ]

        for i in range(countFindItems):
            slot = Movie_Open_Entity.getMovieSlot("%d" % (i))
            gen_mask = fan_group.generateObject("Gen_BlackMask%d" % (i), "Sprite_Black")
            #            self.generedObjects.append(gen_mask)

            gen_mask_entity = gen_mask.getEntity()
            slot.addChild(gen_mask_entity)

            gen_socked = fan_group.generateObject("Gen_Socket%d" % (i), "Socket_Circle")
            #            self.generedObjects.append(gen_socked)
            gen_socked_entity = gen_socked.getEntity()
            slot.addChild(gen_socked_entity)

            gen_socked.setInteractive(True)

            #            self.socets.append(gen_socked)
            #            self.item_linked_socket[ObjList[i]] = gen_socked
            pass

        pass
