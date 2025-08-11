from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class ItemUseManager(Manager):
    manager_dict = {}

    class ItemUse(object):
        def __init__(self, ItemName, SocketGroupName, SocketName, MovieGroupName, MovieName, PopItemName):
            self.ItemName = ItemName
            self.MovieName = MovieName
            self.MovieGroupName = MovieGroupName
            self.PopItemName = PopItemName
            self.SocketName = SocketName
            self.SocketGroupName = SocketGroupName

        def getPopItem(self):
            return self.PopItemName

        def getMovie(self):
            if self.MovieName is None or self.MovieGroupName is None:
                return None
            MovieGroup = GroupManager.getGroup(self.MovieGroupName)
            Movie_Object = MovieGroup.getObject(self.MovieName)
            return Movie_Object

        def getSocket(self):
            if self.SocketName is None or self.SocketGroupName is None:
                return None
            SocketGroup = GroupManager.getGroup(self.SocketGroupName)
            Socket_Object = SocketGroup.getObject(self.SocketName)
            return Socket_Object

    @staticmethod
    def _onFinalize():
        ItemUseManager.manager_dict = {}
        pass

    @staticmethod
    def loadItems(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ItemName = record.get("ItemName")
            SocketGroupName = record.get("SocketGroupName")
            SocketName = record.get("SocketName")
            MovieName = record.get("MovieName")
            MovieGroupName = record.get("MovieGroupName")
            PopItemName = record.get("PopItemName")
            ItemUseManager.addRow(ItemName, SocketGroupName, SocketName, MovieGroupName, MovieName, PopItemName)

    @staticmethod
    def addRow(ItemName, SocketGroupName, SocketName, MovieGroupName, MovieName, PopItemName):
        if not ItemName or not SocketName:
            Trace.log("Manager", 0, "ItemUseManager addRow: input key data error")

        useItem = ItemUseManager.ItemUse(ItemName, SocketGroupName, SocketName, MovieGroupName, MovieName, PopItemName)
        key = ItemName
        subkey = SocketName  # {ItemName:{SocketName:classObj,SocketAnotherName:classObj}}
        sub_dict = {}
        sub_dict[subkey] = useItem
        ItemUseManager.manager_dict[key] = sub_dict
        pass

    @staticmethod
    def hasItem(ItemName):
        return ItemName in ItemUseManager.manager_dict
        pass

    @staticmethod
    def hasSocket(ItemName, SocketName):
        return SocketName in ItemUseManager.manager_dict[ItemName]
        pass

    @staticmethod
    def getItem(ItemName, SocketName):
        if ItemUseManager.hasItem(ItemName) is False or ItemUseManager.hasSocket(ItemName, SocketName) is False:
            Trace.log("ItemUseManager.getItem: not found item %s or couple with Socket %s" % (ItemName, SocketName), 0, '')
            return None

        item = ItemUseManager.manager_dict[ItemName][SocketName]
        return item
        pass

    @staticmethod
    def getMovie(ItemName, SocketName):
        record = ItemUseManager.getItem(ItemName, SocketName)
        if record is None:
            return

        return record.getMovie()
        pass

    @staticmethod
    def getSocket(ItemName, SocketName):
        record = ItemUseManager.manager_dict[ItemName][SocketName]
        return record.getSocket()
        pass

    @staticmethod
    def getPopItem(ItemName, SocketName):
        record = ItemUseManager.getItem(ItemName, SocketName)
        if not record:
            return
        return record.getPopItem()

    @staticmethod
    def getParam(ItemName, SocketName, param):
        record = ItemUseManager.getItem(ItemName, SocketName)
        if record is None:
            return
            pass

        return record.__dict__[param]
