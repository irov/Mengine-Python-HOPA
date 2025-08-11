from Foundation.ArrowManager import ArrowManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.AttachOverViewManager import AttachOverViewManager
from HOPA.ChapterManager import ChapterManager
from HOPA.OverViewManager import OverViewManager
from Notification import Notification


class SystemOverView(System):
    noficators = {
        'ObjectSocket': (Notificator.onSocketMouseEnter, Notificator.onSocketMouseLeave),
        'ObjectTransition': (Notificator.onTransitionMouseEnter, Notificator.onTransitionMouseLeave),
        'ObjectZoom': (Notificator.onZoomMouseEnter, Notificator.onZoomMouseLeave)
    }

    def __init__(self):
        super(SystemOverView, self).__init__()
        self.Freeze = False
        self.Views = []
        self.FinalParagraphs = {}
        pass

    def _onSave(self):
        return (self.Views, self.FinalParagraphs)
        pass

    def _onLoad(self, data_save):
        self.Views, self.FinalParagraphs = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onOverView, self.__StartView)  # args key
        self.addObserver(Notificator.onParagraphComplete, self.__paragraphFilter)
        self.addObserver(Notificator.onTransitionBegin, self.__onTransitionBegin)

        self.applyImmediatelyView()

        for pair in SystemOverView.noficators.values():
            myNotify, myNotifyLeave = pair
            self.addObserver(myNotify, self.__ObjectFilter)
            self.addObserver(myNotifyLeave, self.__LeaveFilter)
            pass
        return True
        pass

    def __onTransitionBegin(self, sceneFrom, sceneTo, ZoomGroupName):
        Notification.notify(Notificator.onOverViewLeave)
        return False
        pass

    def __StartView(self, ViewID, FinalParagraphs):
        myObject = None
        if AttachOverViewManager.hasAnyView(ViewID):
            myObject = AttachOverViewManager.getAnyViewObject(ViewID)
            # myObject.setInteractive(True)
            self.Views.append(myObject)
            pass

        elif OverViewManager.hasView(ViewID):
            myObject = OverViewManager.getObject(ViewID)
            myObject.setInteractive(True)
            self.Views.append(myObject)

        if myObject is not None:
            for i in FinalParagraphs:
                self.FinalParagraphs[i] = myObject
                pass
            pass
        return False
        pass

    def __paragraphFilter(self, ParagraphID):
        if ParagraphID in self.FinalParagraphs:
            myObject = self.FinalParagraphs.pop(ParagraphID)
            self.Views.remove(myObject)
            return False
            pass
        else:  # if already complete
            currentChapter = ChapterManager.getCurrentChapter()
            for paragraphId in self.FinalParagraphs:
                if currentChapter.isParagraphComplete(paragraphId) is True:
                    myObject = self.FinalParagraphs.pop(ParagraphID)
                    self.Views.remove(myObject)
                    pass
                pass
            pass
        return False
        pass

    def showViewMovie(self, MovieObj, movieLoop, viewID=None):
        if TaskManager.existTaskChain("OverView"):
            return
            pass

        MovieObj.setEnable(True)
        MovieWait = not movieLoop
        MovieObj.setLoop(movieLoop)

        isFindItem = OverViewManager.getIfFindItemByID(viewID)
        if isFindItem:
            viewObject = OverViewManager.getObject(viewID)

        with TaskManager.createTaskChain(Name="OverView", Cb=self.unFreze) as tc:
            tc.addEnable(MovieObj)

            if isFindItem:
                with tc.addRaceTask(2) as (tc_play, tc_skip):
                    tc_play.addTask("TaskMoviePlay", Movie=MovieObj, Wait=True)
                    tc_play.addNotify(Notificator.OnOverViewShowed, viewID)
                    tc_play.addFunction(self._removeView, viewObject)

                    tc_skip.addListener(Notificator.onOverViewLeave)
                    tc_skip.addFunction(self.unFreze, False)
                    pass
                tc.addDisable(MovieObj)
                pass
            else:
                tc.addTask("TaskMoviePlay", Movie=MovieObj, Wait=MovieWait, LastFrame=MovieWait)
                if movieLoop:
                    tc.addListener(Notificator.onOverViewLeave)
                    tc.addFunction(MovieObj.setEnable, False)
                    tc.addFunction(self.unFreze, False)
                    pass
                pass
        pass

    def __TakeView(self, Object):
        Item = ArrowManager.getArrowAttach()
        key = Object.getName()
        if Item is not None:
            SingleOverView = AttachOverViewManager.getView(key)
            if SingleOverView is not None:
                MovieObj = SingleOverView.getMovie()
                movieLoop = SingleOverView.getLoop()
                self.showViewMovie(MovieObj, movieLoop, key)
                return False
                pass

            ItemEntity = Item.getEntity()
            ItemName = ItemEntity.getName()
            SingleAttachOverView = AttachOverViewManager.getView(key, ItemName)
            if SingleAttachOverView is not None:
                MovieObj = SingleAttachOverView.getMovie()
                movieLoop = SingleAttachOverView.getLoop()
                self.showViewMovie(MovieObj, movieLoop, key)
                return False
                pass

        if self.Freeze:
            return False

        if OverViewManager.hasView(key):
            self.Freeze = True
            MovieObj = OverViewManager.getMovie(key)
            movieLoop = OverViewManager.getLoop(key)
            self.showViewMovie(MovieObj, movieLoop, key)
            return False
            pass

        return False
        pass

    def unFreze(self, isSkip):
        self.Freeze = False
        pass

    def getNotification(self, Object):
        type = Object.__class__.__name__
        if type in SystemOverView.noficators:
            return SystemOverView.noficators[type]
        return False
        pass

    def __ObjectFilter(self, Object):
        if Object in self.Views:
            self.__TakeView(Object)
            pass
        return False
        pass

    def __LeaveFilter(self, Object):
        if Object in self.Views:
            Notification.notify(Notificator.onOverViewLeave)
            pass
        return False
        pass

    def _onStop(self):
        self.Views = []
        self.FinalParagraphs = {}
        pass

    def applyImmediatelyView(self):
        viewIds = OverViewManager.getImmediatelyEntries()

        for viewId in viewIds:
            self.__StartView(viewId, [])
            pass

        itemViewsIds = AttachOverViewManager.getAllViews()
        for viewId in itemViewsIds:
            self.__StartView(viewId, [])
            pass

        pass

    def insertViewer(self, ViewID, ObjectName, MovieGroupName, MovieName, Enable=False, Loop=None, SubObject=None):
        # insert from another entity or system and immediatly start view
        OverViewManager.loadViewer(ViewID, ObjectName, MovieGroupName, MovieName, Enable, Loop, SubObject, None)
        self.__StartView(ViewID, [])
        pass

    def _removeView(self, object):
        if object in self.Views:
            self.Views.remove(object)
            pass
        pass
