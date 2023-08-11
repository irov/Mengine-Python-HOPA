from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.TipManager import TipManager
from Foundation.Notificator import Notificator


class MacroElementalMagicGet(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True and len(values) < 3:
            self.initializeFailed(
                "{!r} not add all params, group {}:{}".format(self.CommandType, self.GroupName, self.Index))

        self.socket_name = values[0]
        self.elemental_magic_id = values[1]
        self.tip_id = values[2]

        # self.Inventory = None
        # self.InventoryItemObject = None
        self.socket_obj = None

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            # check socket
            if self.hasObject(self.socket_name) is False:
                self.initializeFailed(
                    "{!r} not found object {!r} in group {!r}".format(self.CommandType, self.socket_name,
                                                                      self.GroupName))
            # # check elemental magic
            # if ElementalMagicManager.hasMagic(self.elemental_magic_id) is False:
            #     self.initializeFailed("ElementalMagic %s not found in ElementalMagic.xlsx" % self.elemental_magic_id)
            #
            # if ElementalMagicManager.isActiveMagic(self.elemental_magic_id) is False:
            #     self.initializeFailed("ElementalMagic %s is not active" % self.elemental_magic_id)

            # check tip
            if TipManager.hasTip(self.tip_id) is False:
                self.initializeFailed("Tip {!r} not found".format(self.tip_id))

        _, self.socket_obj = self.findObject(self.socket_name)

        # self.InventoryItemObject = ItemManager.getItemInventoryItem(self.ElementalMagicId)
        # self.Inventory = DemonManager.getDemon("Inventory")

    # def _onGenerate(self, source):
    #     Quest = self.addQuest(source, "UseInventoryItem", SceneName=self.SceneName, GroupName=self.GroupName,
    #                           Object=self.socket_obj)
    #
    #     with Quest as tc_quest:
    #         tc_quest.addNotify(Notificator.onTipActivateWithoutParagraphs, self.socket_obj, self.tip_id)
    #         tc_quest.addTask("AliasGiveItem", Object=self.socket_obj, SocketName=self.socket_name,
    #                          ItemName=self.elemental_magic_id, TipName=self.tip_id)
    #         tc_quest.addNotify(Notificator.onTipRemoveWithoutParagraphs, self.tip_id)
    #
    #     source.addListener(Notificator.onInventoryUpdateItem)
