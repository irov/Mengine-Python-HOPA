from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class FeedStatesManager(object):
    feeds = {}

    class SingleFeeder(object):
        def __init__(self):
            self.movie_heap = []
            self.ref = []
            self.sockets = []
            self.limits = []
            self.sprites = []
            pass

        def getRef(self):
            return self.ref
            pass

        def addRow(self, movies, ref, socket, limit, sprite):
            self.ref.append(ref)
            self.sockets.append(socket)
            self.movie_heap.append(movies)
            self.limits.append(limit)
            self.sprites.append(sprite)
            pass

        def getMovieStates(self):
            return self.movie_heap
            pass

        def getSockets(self):
            return self.sockets

        def getLimits(self):
            return self.limits

        def getSprites(self):
            return self.sprites

        pass

    @staticmethod
    def onFinalize():
        FeedStatesManager.feeds.clear()
        pass

    @staticmethod
    def loadItems(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            name = record.get("Name")
            demon_name = record.get("Demon")
            group_name = record.get("Group")
            table_name = record.get("Table")
            FeedStatesManager.addRow(table_name, group_name, demon_name, name)
            pass
        pass

    @staticmethod
    def addRow(module, param, group_name, demon_name, name):
        demon = GroupManager.getObject(group_name, demon_name)
        records = DatabaseManager.getDatabaseRecords(module, param)
        feeder = FeedStatesManager.SingleFeeder()
        for record in records:
            Idle = record.get("Idle")
            Eat = record.get("Eat")
            Passive = record.get("Passive")
            Active = record.get("Active")
            Away = record.get("Away")
            Ref = record.get("Ref")
            Socket = record.get("Socket")
            Limit = record.get("Limit")
            Sprite = record.get("Sprite")
            socket_object = Socket  # demon.getObject(Socket)
            movie_names = [Idle, Eat, Away, Passive, Active]
            movie_objects = [demon.getObject(names) for names in movie_names]
            sprite = demon.getObject(Sprite)
            feeder.addRow(movie_objects, Ref, socket_object, Limit, sprite)
            pass
        FeedStatesManager.feeds[name] = feeder
        pass

    @staticmethod
    def hasDemon(DemonName):
        return DemonName in FeedStatesManager.feeds
        pass

    @staticmethod
    def getFeeder(DemonName):
        if not FeedStatesManager.hasDemon(DemonName):
            Trace.log("FeedStatesManager : not found item %s " % (DemonName), 0, '')
            return False
        return FeedStatesManager.feeds[DemonName]
        pass

    @staticmethod
    def getMovieStates(DemonName):
        detector = FeedStatesManager.getFeeder(DemonName)
        return detector.getMovieStates()

    @staticmethod
    def getRef(DemonName):
        detector = FeedStatesManager.getFeeder(DemonName)
        return detector.getRef()
        pass

    @staticmethod
    def getSockets(DemonName):
        detector = FeedStatesManager.getFeeder(DemonName)
        return detector.getSockets()
        pass

    @staticmethod
    def getLimits(DemonName):
        detector = FeedStatesManager.getFeeder(DemonName)
        return detector.getLimits()

    @staticmethod
    def getSprites(DemonName):
        detector = FeedStatesManager.getFeeder(DemonName)
        return detector.getSprites()
