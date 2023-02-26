from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

from TraceManager import TraceManager

class AttachOverViewManager(object):
    bound_attached_dict = {}  # (itemName,objectName)->SOV
    attached_dict = {}  # objectName->SOV

    ObjectNameList = {}

    class SingleOverView(object):

        def __init__(self, ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject):
            self.ObjectName = ObjectName
            self.MovieGroupName = MovieGroupName
            self.MovieName = MovieName
            self.Loop = Loop
            self.SubObject = SubObject
            self.Enable = Enable or self.__disable()

        pass

        def getMovie(self):
            movieObj = self.__get_object(self.MovieName)
            return movieObj
            pass
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
        AttachOverViewManager.bound_attached_dict = {}
        pass

    @staticmethod
    def loadParams(module, param):
        TraceManager.addTrace("AttachOverViewManager")
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ObjectName = record.get("ObjectName")
            MovieGroupName = record.get("MovieGroupName")
            MovieName = record.get("MovieName")
            Enable = record.get("EnableDefault")
            Loop = record.get("Loop")
            SubObject = record.get("SubObject")
            ItemsList = record.get("Item")
            AttachOverViewManager.loadViewer(ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject, ItemsList)
            pass
        pass

    @staticmethod
    def loadViewer(*params):
        ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject, ItemsList = params

        if not ObjectName or not MovieGroupName or not MovieGroupName:
            Trace.log("AttachOverViewManager", 0, "AttachOverViewManager.loadViewer: : invalid param")
            return
            pass

        data = AttachOverViewManager.SingleOverView(ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject)
        if ItemsList is None:
            AttachOverViewManager.attached_dict[ObjectName] = data
            AttachOverViewManager.ObjectNameList[ObjectName] = data.getObject()
            return
            pass

        else:
            AttachOverViewManager.bound_attached_dict[(ObjectName, ItemsList)] = data
            pass

        AttachOverViewManager.ObjectNameList[ObjectName] = data.getObject()
        pass

    @staticmethod
    def hasView(ViewID, ItemName=None):
        if ItemName is None:
            hasView = ViewID in AttachOverViewManager.attached_dict
            return hasView
            pass
        hasView = (ViewID, ItemName) in AttachOverViewManager.bound_attached_dict
        return hasView
        pass

    @staticmethod
    def hasAnyView(ViewId):
        if ViewId in AttachOverViewManager.ObjectNameList:
            return True
            pass
        return False
        pass

    @staticmethod
    def getAnyViewObject(ViewId):
        if AttachOverViewManager.hasAnyView(ViewId) is False:
            Trace.log("AttachOverViewManager", 0, "AttachOverViewManager.getAnyViewObject: : invalid param")
            return None
            pass

        object = AttachOverViewManager.ObjectNameList[ViewId]
        return object
        pass

    @staticmethod
    def getView(ViewID, ItemName=None):
        if AttachOverViewManager.hasView(ViewID, ItemName) is False:
            # Trace.log("AttachOverViewManager", 0, "AttachOverViewManager.getView: : invalid param")
            return None
            pass

        if ItemName is None:
            view = AttachOverViewManager.attached_dict[ViewID]
            return view
            pass

        view = AttachOverViewManager.bound_attached_dict[(ViewID, ItemName)]
        return view
        pass

    @staticmethod
    def getMovie(ViewID, ItemName=None):
        view = AttachOverViewManager.getView(ViewID, ItemName)
        return view.getMovie()
        pass

    @staticmethod
    def getLoop(ViewID, ItemName=None):
        view = AttachOverViewManager.getView(ViewID, ItemName)
        return view.getLoop()
        pass

    @staticmethod
    def getObject(ViewID, ItemName=None):
        view = AttachOverViewManager.getView(ViewID, ItemName)
        return view.getObject()
        pass

    @staticmethod
    def getAllViews():
        views = []
        views.extend(AttachOverViewManager.bound_attached_dict.values())
        views.extend(AttachOverViewManager.attached_dict.values())
        ObjectNameList = AttachOverViewManager.ObjectNameList.keys()
        return ObjectNameList
        pass

#    @staticmethod
#    def getImmediatelyEntries():
#        return AttachOverViewManager.immediately
#        pass