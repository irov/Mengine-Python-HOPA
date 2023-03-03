from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroAddItem(MacroCommand):
    def __init__(self):
        super(MacroAddItem, self).__init__()

        self.ItemName = None
        self.FromPointName = None
        self.IsFromPointTuple = False
        self.FromPoint = None

    def _onValues(self, values, **params):
        self.ItemName = values[0]

        self.IsFromPointTuple = False

        if len(values) > 1:  # second arg can be FromPointName (name of ObjectPoint) or tuple(float_x, float_y)

            parsed_floats = []
            for i in values[1].split(", "):
                try:
                    val = float(i)
                    parsed_floats.append(val)
                except ValueError:
                    break

            b_is_point_tuple_valid = len(parsed_floats) >= 2 and isinstance(parsed_floats[0], float) and isinstance(
                parsed_floats[1], float)

            if b_is_point_tuple_valid:  # from point should be tuple
                self.IsFromPointTuple = True
                self.FromPoint = (parsed_floats[0], parsed_floats[1])

            else:
                self.FromPointName = values[1]  # from point should be type of ObjectPoint

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if self.ItemName is None:
                self.initializeFailed("Item is None")

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName))

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))

            if self.IsFromPointTuple and isinstance(self.FromPoint, tuple):  # don't process FromPoint as ObjectPoint
                return

            if self.FromPointName is None:
                return

            # get FromPoint if it's meant to be type of ObjectPoint
            if GroupManager.hasObject(self.GroupName, self.FromPointName) is False:
                self.initializeFailed("Object %s not found in group %s" % (self.FromPointName, self.GroupName))
                return
            pass

        if self.IsFromPointTuple and isinstance(self.FromPoint, tuple):  # don't process FromPoint as ObjectPoint
            return

        if self.FromPointName is None:
            return

        self.FromPoint = GroupManager.getObject(self.GroupName, self.FromPointName)

        if _DEVELOPMENT is True:
            if self.FromPoint.getType() != "ObjectPoint":
                self.initializeFailed("Object %s is not a ObjectPoint" % (self.FromPointName))

    def _onGenerate(self, source):
        Inventory = DemonManager.getDemon("Inventory")

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        Quest = self.addQuest(source, "AddItem", SceneName=self.SceneName, GroupName=self.GroupName)

        with Quest as tc_quest:
            tc_quest.addTask("TaskNotify", ID=Notificator.onInventoryRise)
            tc_quest.addNotify(Notificator.onSoundEffectOnObject, InventoryItem, "AddItem")

            with GuardBlockInput(tc_quest) as guard_source:
                if self.FromPoint is None:
                    guard_source.addTask("AliasInventoryAddInventoryItem", Inventory=Inventory, ItemName=self.ItemName)
                else:
                    guard_source.addTask("AliasInventoryAddInventoryItemFromPoint", Inventory=Inventory,
                                         ItemName=self.ItemName, FromPoint=self.FromPoint)
