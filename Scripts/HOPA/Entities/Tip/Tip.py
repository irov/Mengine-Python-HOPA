from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from HOPA.TipManager import TipManager
from Notification import Notification


class Tip(BaseEntity):
    TIP_SHOW = 1
    TIP_HIDE = 2

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "FixedPoint")
        Type.addAction(Type, "PlayPolicy")
        pass

    def __init__(self):
        super(Tip, self).__init__()

        self.state = Tip.TIP_HIDE
        self.tipID = None

        self.skippedTipID = None
        pass

    def _onRestore(self):
        if self.object.hasObject("Sprite_BlackBar"):
            Sprite_BlackBar = self.object.getObject("Sprite_BlackBar")
            Sprite_BlackBar.setEnable(False)
            pass

        Text_Message = self.object.getObject("Text_Message")
        Text_Message.setEnable(False)
        pass

    def _onDeactivate(self):
        super(Tip, self)._onDeactivate()

        if TaskManager.existTaskChain("TipPlay"):
            TaskManager.skipTaskChain("TipPlay")
            pass

        self.state = Tip.TIP_HIDE

        Notification.removeObserver(self.onTipShow)
        Notification.removeObserver(self.onBlackBarRelease)
        Notification.removeObserver(self.onSceneChange)
        # Notification.removeObserver(self.onZoomClose)
        pass

    def _onActivate(self):
        super(Tip, self)._onActivate()

        self.TipShowTime = DefaultManager.getDefaultFloat("TipShowTime", 3)
        self.TipShowTime *= 1000  # speed fix

        self.policy = PolicyManager.getPolicy("TipPlay", "PolicyBlackBarPlayStatic")
        self.moviePolicy = PolicyManager.getPolicy("TipPlayMovie", "PolicyBlackBarPlayStaticWithMovie")

        self.onTipShow = Notification.addObserver(Notificator.onTipShow, self.showBlackBar)
        self.onBlackBarRelease = Notification.addObserver(Notificator.onBlackBarRelease, self.releaseBlackBar)
        self.onSceneChange = Notification.addObserver(Notificator.onSceneChange, self.__onSceneChange)
        # self.onZoomClose = Notification.addObserver(Notificator.onZoomClose, self.releaseBlackBar)

        pass

    def showBlackBar(self, TipID):
        if self.tipID == TipID:
            return False
            pass

        if self.skippedTipID is not None and self.skippedTipID == TipID:
            isSkipStart = True
        else:
            isSkipStart = False

        self.skippedTipID = None

        Notification.notify(Notificator.onBlackBarRelease, True)

        TextID = TipManager.getTextID(TipID)

        self.tipID = TipID
        tipMovie = None

        if TipManager.isMovieTip(TipID) is True:
            tipMovie = TipManager.getMovieTip(TipID)
            pass

        with TaskManager.createTaskChain(Name="TipPlay", Group=self.object, Cb=self._onTipShowComplete) as tc:
            if tipMovie is not None:
                # print "TipID",TipID
                # tc.addPrint("tipMovie is not None")
                tc.addTask(self.moviePolicy, TextID=TextID, Time=self.TipShowTime, Movie=tipMovie)
                pass
            elif self.PlayPolicy is not None:
                # print "TipID", TipID
                # tc.addPrint("elif self.PlayPolicy is not None")
                tc.addTask(self.PlayPolicy, TextID=TextID, Time=self.TipShowTime)
                pass
            elif tipMovie is None:
                # print "TipID", TipID
                # tc.addPrint("elif tipMovie is None")
                tc.addTask(self.policy, TextID=TextID, Time=self.TipShowTime, SkipStart=isSkipStart)
                pass
            pass

        self.state = Tip.TIP_SHOW

        return False
        pass

    def _onTipShowComplete(self, isSkip):
        # print "!!!!!!!!!!!!!!! _onTipShowComplete isSkip=", isSkip

        if isSkip is True:
            self.skippedTipID = self.tipID
        else:
            self.skippedTipID = None

        Notification.notify(Notificator.onTipPlayComplete, self.tipID, self.object)

        self.state = Tip.TIP_HIDE
        self.tipID = None
        pass

    def releaseBlackBar(self, currentID=None):
        # if self.tipID == currentID:
        #     return False
        #     pass

        if TaskManager.existTaskChain("TipPlay"):
            TaskManager.cancelTaskChain("TipPlay")
            pass

        self.state = Tip.TIP_HIDE
        return False
        pass

    def __onSceneChange(self, SceneName_From):
        Notification.notify(Notificator.onBlackBarRelease, self.tipID)
        return False

    pass
