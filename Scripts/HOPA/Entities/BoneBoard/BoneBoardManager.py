from Foundation.DatabaseManager import DatabaseManager

class BoneBoardManager(object):
    s_objects = {}
    macro_names = {}
    data = {}

    class Bone(object):
        def __init__(self, items, prev, inv_items, movie_add, movie_use, movie_wrong):
            self.items = items
            self.prev = prev
            self.inv_items = inv_items
            self.movie_add = movie_add
            self.movie_use = movie_use
            self.movie_wrong = movie_wrong
            pass

    @staticmethod
    def onFinalize():
        BoneBoardManager.s_objects = {}
        BoneBoardManager.macro_names = {}
        BoneBoardManager.data = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        items = []
        prev = []
        inv = []
        mu = []
        mw = []
        ma = []
        mo = []
        for values in records:
            itemName = values.get("Item")
            items.append(itemName)

            prevName = values.get("Mask")
            inventoryName = values.get("Name")
            prev.append([prevName, inventoryName])
            inv.append(inventoryName)
            movie_add = values.get("Movie_Add")
            movie_use = values.get("Movie_Use")
            movie_wrong = values.get("Movie_Wrong")
            movie_over = values.get("Movie_Over")
            mu.append(movie_use)
            mw.append(movie_wrong)
            ma.append(movie_add)
            if movie_over is not None:
                mo.append(movie_over)
                pass

            group = values.get("Group")
            BoneBoardManager.macro_names[inventoryName] = itemName

            BoneBoardManager.loadCollection(items, prev, inv, ma, mu, mw, mo, group)
            pass
        pass

    @staticmethod
    def loadCollection(items, prev, inv, movie_add, movie_use, movie_wrong, movies_over, group):
        BoneBoardManager.data = dict(Group=group, MoviesOver=movies_over, MoviesAdd=movie_add, MoviesUse=movie_use, MoviesWrong=movie_wrong, Items=items, Preview=prev, InventoryItems=inv)
        pass

    @staticmethod
    def getPrev():
        newList = []
        previews = BoneBoardManager.data["Preview"]
        for data in previews:
            newList.append(data[0])
            pass
        return newList
        pass

    @staticmethod
    def delPrev(name):
        prev = BoneBoardManager.data["Preview"]
        for data in prev:
            if data[1] == name:
                data[0] = None
                break
                pass
            pass
        pass

    @staticmethod
    def getMovieAdd():
        moviesAdd = BoneBoardManager.data["MoviesAdd"]
        return moviesAdd
        pass

    @staticmethod
    def getMovieWrong():
        MoviesWrong = BoneBoardManager.data["MoviesWrong"]
        return MoviesWrong
        pass

    @staticmethod
    def getMovieUse():
        MoviesUse = BoneBoardManager.data["MoviesUse"]
        return MoviesUse
        pass

    @staticmethod
    def getMovieOver():
        MoviesOver = BoneBoardManager.data["MoviesOver"]
        return MoviesOver
        pass

    @staticmethod
    def getItems():
        Items = BoneBoardManager.data["Items"]
        return Items
        pass

    @staticmethod
    def getGroup():
        Group = BoneBoardManager.data["Group"]
        return Group
        pass

    @staticmethod
    def getInvItem():
        InventoryItems = BoneBoardManager.data["InventoryItems"]
        return InventoryItems
        pass

    @staticmethod
    def getItemName(exelEntrie):
        return BoneBoardManager.macro_names.get(exelEntrie)
        pass

    @staticmethod
    def getSocketName(exelEntrie):
        item_name = BoneBoardManager.getItemName(exelEntrie)
        Items = BoneBoardManager.data["Items"]
        index = Items.index(item_name)
        previews = BoneBoardManager.data["Preview"]
        socket_name = previews[index][0]
        return socket_name
        pass
    pass