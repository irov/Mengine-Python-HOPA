from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.MindManager import MindManager
from Notification import Notification


class SystemMindGroup(System):
    def __init__(self):
        super(SystemMindGroup, self).__init__()
        self.Groups = {}
        self.Sprite_BlackBar = None
        self.tc = None
        self.Start = False
        self.IsWorking = False

    def _onRun(self):
        # print " SystemMindGroup _onRun"
        SpriteName = "Sprite_BlackBar"
        self.Demon = DemonManager.getDemon('Tip')
        self.Sprite_BlackBar = self.Demon.getObject(SpriteName)
        self.Sprite_BlackBar.setEnable(False)

        Allminds = MindManager.getAllMinds()
        for key in Allminds:
            if Allminds[key].group != None:
                self.Groups[Allminds[key].group] = key  # print " self.Groups[Allminds[key].group]=key",self.Groups

        self.addObserver(Notificator.onGroupEnable, self._MindShow)
        self.addObserver(Notificator.onZoomOpen, self._MindShow)
        self.addObserver(Notificator.onGroupDisable, self.__onGroupDisable)
        self.addObserver(Notificator.onGroupEnableMacro, self.__onGroupEnable)
        self.addObserver(Notificator.onBlackBarRelease, self.__onMindShowComplete)
        self.addObserver(Notificator.onZoomClose, self.__onZoomClose)
        self.addObserver(Notificator.onMindEndlessEnd, self._MindOff_Notify)
        self.addObserver(Notificator.onShowMindByID, self.__cbShowMindByID)

        return True
        pass

    def __cbShowMindByID(self, mind_id):
        # print '__CbShowMindByID', mind_id
        self.Start = True
        self.__showBlackBar(mind_id)

        return False

    def _MindShow(self, GroupName=None, Starter=False):
        # print "_MindShow", GroupName,Starter

        if Starter is True:
            self.Start = True

        if self.Start is False:
            # print "self.Start is False"
            return False

        if GroupName not in self.Groups:
            # print "GroupName not in self.Groups", self.Groups
            return False

        # print "SystemMindGroup _Reaction ,a,b,c", GroupName, Starter
        # print "SystemMindGroup _Reaction  self.Groups", self.Groups

        mindId = self.Groups[GroupName]
        self.__showBlackBar(mindId)

        return False

    def __onGroupEnable(self, GroupName):
        self.Start = True
        self._MindShow(GroupName, True)
        return False

    def __showBlackBar(self, mindId):
        Notification.notify(Notificator.onBlackBarRelease, "Some Arg")
        self.__onMindShowComplete()
        self.IsWorking = True
        TextID = MindManager.getTextID(mindId)
        delay = MindManager.getDelay(mindId)
        # if delay==0:
        #     delay=9999999999999.9
        # print "TextID",TextID,mindId, delay

        self.tc = TaskManager.createTaskChain(Repeat=False, Cb=self._MindOff)
        with self.tc as tc:
            tc.addTask("TaskTextSetTextID", Group=self.Demon, TextName="Text_Message", Value=TextID)
            tc.addTask("TaskEnable", Group=self.Demon, ObjectName="Text_Message", Value=False)
            tc.addDisable(self.Sprite_BlackBar)
            tc.addEnable(self.Sprite_BlackBar)
            tc.addTask("TaskEnable", Group=self.Demon, ObjectName="Text_Message", Value=True)
            tc.addFunction(self.attachText)
            tc.addTask("AliasObjectAlphaTo", Object=self.Sprite_BlackBar, Time=1000, From=0.0, To=1.0)

            tc.addTask("TaskEnable", Group=self.Demon, ObjectName="Text_Message", Value=True)
            with tc.addIfTask(lambda: delay == 0) as (true, false):
                true.addListener(Notificator.onZoomClose)
                false.addDelay(delay)
            tc.addDelay(delay)

            tc.addDisable(self.Sprite_BlackBar)
            tc.addTask("TaskEnable", Group=self.Demon, ObjectName="Text_Message", Value=False)

        return False
        pass

    def __onZoomClose(self, GroupName=None):
        self._MindOff()
        return False

    def __onGroupDisable(self, GroupName):
        self._MindOff()
        return False

    def _MindOff_Notify(self):
        # print "_MindOff_Notify"
        self.Start = False
        self._MindOff()
        return False

    def _MindOff(self, isSkip=False):
        if isSkip is True:
            return False
        if self.IsWorking is False:
            return False

        self.__onMindShowComplete()

        self.tc = TaskManager.createTaskChain(Repeat=False, Cb=self.__cbMindOff)
        with self.tc as tc:
            tc.addEnable(self.Sprite_BlackBar)
            tc.addTask("TaskEnable", Group=self.Demon, ObjectName="Text_Message", Value=True)
            tc.addFunction(self.attachText)
            tc.addTask("AliasObjectAlphaTo", Object=self.Sprite_BlackBar, Time=0.1 * 10000, To=0.0)  # spees fix
            tc.addFunction(self.deattachText)
            tc.addDisable(self.Sprite_BlackBar)
            tc.addTask("TaskEnable", Group=self.Demon, ObjectName="Text_Message", Value=False)

            # tc.addFunction(self.__onMindShowComplete)

        return False

    def __cbMindOff(self, isSkip):
        self.tc = None
        self.IsWorking = False

    def __onMindShowComplete(self, Cb=None, Cb2=None):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None
        self.IsWorking = False
        return False
        pass

    def attachText(self):
        if self.Sprite_BlackBar.isActive() is False:
            return
        Group = self.Demon
        NodeForText = self.Sprite_BlackBar.getEntityNode()

        TextBox = Group.getObject("Text_Message")
        TextEntityNode = TextBox.getEntityNode()
        NodeForText.addChild(TextEntityNode)
        pass

    def deattachText(self):
        if self.Demon.isActive() is False:
            return
        Group = self.Demon
        TextBox = Group.getObject("Text_Message")
        TextEntity = TextBox.getEntity()
        TextEntity.removeFromParent()
        pass

    def _onStop(self):
        self.Groups = {}
        self.Start = False
        pass

    def _onSave(self):
        return (self.Start,)
        pass

    def _onLoad(self, data_save):
        self.Start = data_save
        pass
