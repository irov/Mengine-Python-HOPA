from HOPA.ItemManager import ItemManager

class InventoryItemUseMovieManager(object):
    s_inventoryItems = {}

    class InventoryItem(object):
        def __init__(self, group, movieName):
            self.group = group
            self.movieName = movieName
            pass
        pass

    @staticmethod
    def onFinalize():
        InventoryItemUseMovieManager.s_inventoryItems = {}
        pass

    @staticmethod
    def loadParam(param):
        InventoryItemUseMovie_Param = Mengine.getParam(param)

        if InventoryItemUseMovie_Param is None:
            Trace.log("Manager", 0, "InventoryItemUseMovieManager.loadParam: invalid param %s" % (param))
            return

        for values in InventoryItemUseMovie_Param:
            groupName = values[0].strip()

            if groupName == "":
                continue

            inventoryItemName = values[1].strip()
            movieName = values[2].strip()
            InventoryItemUseMovieManager.addInventoryItem(inventoryItemName, groupName, movieName)
            pass
        pass

    @staticmethod
    def addInventoryItem(inventoryItemName, groupName, movieName):
        if inventoryItemName in InventoryItemUseMovieManager.s_inventoryItems:
            Trace.log("Manager", 0, "InventoryItemUseMovieManager addInventoryItem: item %s already exist" % (inventoryItemName))
            return
            pass

        movieGroup = GroupManager.getGroup(groupName)
        if movieGroup.hasObject(movieName) == False:
            Trace.log("Manager", 0, "InventoryItemUseMovieManager addInventoryItem: Group %s not found movie %s" % (groupName, movieName))

        inventoryItem = InventoryItemUseMovieManager.InventoryItem(movieGroup, movieName)

        InventoryItemUseMovieManager.s_inventoryItems[inventoryItemName] = inventoryItem

        ObjectInventoryItem = ItemManager.findItemInventoryItem(inventoryItemName)

        if ObjectInventoryItem is None:
            Trace.log("Manager", 0, "InventoryItemUseMovieManager addInventoryItem: Cann't get item '%s'" % (itemName))
            pass
        pass

    @staticmethod
    def getMovie(inventoryItemName):
        if inventoryItemName not in InventoryItemUseMovieManager.s_inventoryItems:
            return None
            pass

        InventoryItem = InventoryItemUseMovieManager.s_inventoryItems[inventoryItemName]

        return [InventoryItem.group, InventoryItem.movieName]
        pass