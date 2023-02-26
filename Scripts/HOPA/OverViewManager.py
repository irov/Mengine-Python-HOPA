from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class OverViewManager(object):
    managment_dict = {}
    immediately = []

    class SingleOverView(object):

        def __init__(self, ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject, isFindItem):
            self.ObjectName = ObjectName
            self.MovieGroupName = MovieGroupName
            self.MovieName = MovieName
            self.Loop = Loop
            self.SubObject = SubObject
            self.Enable = Enable or self.__disable()

            self.isFindItem = isFindItem

        pass

        def getMovie(self):
            movieObj = self.__get_object(self.MovieName)
            return movieObj
            pass
        pass

        def ifFindItem(self):
            return self.isFindItem
            pass

        def __get_object(self, objectName):
            if self.SubObject is not None:
                sub_object = GroupManager.getObject(self.MovieGroupName, self.SubObject)
                _object = sub_object.getObject(objectName)
                pass
            else:
                _object = GroupManager.getObject(self.MovieGroupName, objectName)
                pass
            return _object
            pass

        def getObject(self):
            Object = self.__get_object(self.ObjectName)

            return Object
            pass
        pass

        def __disable(self):
            movie = self.getMovie()
            movie.setEnable(False)
            return False
            pass

        def getLoop(self):
            return bool(self.Loop)

    @staticmethod
    def onFinalize():
        OverViewManager.managment_dict = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ViewID = record.get("ViewID")
            ObjectName = record.get("ObjectName")
            MovieGroupName = record.get("MovieGroupName")
            MovieName = record.get("MovieName")
            Enable = record.get("EnableDefault")
            Loop = record.get("Loop")
            SubObject = record.get("SubObject")
            Immediately = record.get("Immediately")
            isFindItem = record.get("isFindItem")
            OverViewManager.loadViewer(ViewID, ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject, Immediately, isFindItem)
            pass
        pass

    @staticmethod
    def loadViewer(*params):
        ViewID, ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject, Immediately, isFindItem = params

        if not ObjectName or not MovieGroupName or not MovieGroupName:
            Trace.log("OverViewManager", 0, "OverViewManager.loadViewer: : invalid param")
            return
            pass

        data = OverViewManager.SingleOverView(ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject, isFindItem)

        OverViewManager.managment_dict[ViewID] = data

        if Immediately is not None:
            OverViewManager.immediately.append(ViewID)
            pass
        pass

    @staticmethod
    def hasView(ViewID):
        return ViewID in OverViewManager.managment_dict
        pass

    @staticmethod
    def getIfFindItemByID(ViewID):
        view = OverViewManager.getView(ViewID)
        return view.ifFindItem()
        pass

    @staticmethod
    def getView(ViewID):
        if OverViewManager.hasView(ViewID) is False:
            Trace.log("OverViewManager", 0, "OverViewManager.getView: : invalid param")
            return None
            pass

        return OverViewManager.managment_dict[ViewID]
        pass

    @staticmethod
    def getMovie(ViewID):
        view = OverViewManager.getView(ViewID)
        return view.getMovie()
        pass

    @staticmethod
    def getLoop(ViewID):
        view = OverViewManager.getView(ViewID)
        return view.getLoop()
        pass

    @staticmethod
    def getObject(ViewID):
        view = OverViewManager.getView(ViewID)
        return view.getObject()
        pass

    @staticmethod
    def getImmediatelyEntries():
        return OverViewManager.immediately
        pass