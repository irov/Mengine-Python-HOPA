from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.NewspaperManager import NewspaperManager
from HOPA.QuestManager import QuestManager


class Newspaper(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "NewspaperID")
        Type.addAction(Type, "ShowComplete")
        Type.addAction(Type, "Open")
        pass

    def __init__(self):
        super(Newspaper, self).__init__()
        self.AttachGroupName = None
        self.newspaper = None
        self.tempEnableGroups = []
        self.AttachLayerGroup = None
        self.Quest = None
        pass

    def __showNewspaper(self):
        if self.Open is True:
            self.__openNewspaper()
            return
            pass

        SceneName = SceneManager.getCurrentSceneName()
        GroupName = SceneManager.getSceneMainGroupName(SceneName)

        if TaskManager.existTaskChain("Newspaper%s" % (self.NewspaperID)):
            TaskManager.cancelTaskChain("Newspaper%s" % (self.NewspaperID))
            pass

        with TaskManager.createTaskChain(Name="Newspaper%s" % (self.NewspaperID)) as tc:
            self.Quest = QuestManager.createLocalQuest("NewspaperRepeat", SceneName=SceneName,
                                                       GroupName=GroupName, Object=self.newspaper.socket_Open)
            with QuestManager.runQuest(tc, self.Quest) as tc_quest:
                tc_quest.addTask("TaskSocketClick", Socket=self.newspaper.socket_Open)
                tc_quest.addFunction(self.__openNewspaper)
                pass
            pass
        pass

    def __openNewspaper(self):
        if self.NewspaperID is None:
            return

        layerAttachGroupEntity = self.AttachLayerGroup.getEntity()

        movieOpenGroup = self.newspaper.movie_Open.getGroup()
        if movieOpenGroup != self.newspaper.socket_Open.getGroup():
            self.tempEnableGroups.append(movieOpenGroup)
            pass

        movieCloseGroup = self.newspaper.movie_Close.getGroup()
        if movieCloseGroup != self.newspaper.socket_Close.getGroup():
            self.tempEnableGroups.append(movieCloseGroup)
            pass

        for group in self.tempEnableGroups:
            group.onEnable()
            pass

        self.newspaper.movie_Open.setEnable(True)
        self.newspaper.movie_Close.setEnable(True)

        slotMovieOpenEntity = self.newspaper.movie_Open.getEntity()
        slotOpen = slotMovieOpenEntity.getMovieSlot("group")

        slotMovieCloseEntity = self.newspaper.movie_Close.getEntity()
        slotClose = slotMovieCloseEntity.getMovieSlot("group")

        NewspaperFade = DefaultManager.getDefaultFloat("NewspaperFade", 0.5)

        if self.Open is True:
            with TaskManager.createTaskChain(Name="NewspaperOpen%s" % (self.NewspaperID), Cb=self._showComplete) as tc:
                tc.addTask("TaskInteractive", Object=self.newspaper.socket_Close, Value=True)
                tc.addParam(self.newspaper.movie_Open, "LastFrame", False)
                tc.addTask("TaskNodeAddChild", ParentNode=slotOpen, ChildNode=layerAttachGroupEntity)
                tc.addTask("TaskNodeEnable", Node=layerAttachGroupEntity, Value=True)
                tc.addNotify(Notificator.onNewspaperOpen, self.NewspaperID)

                with tc.addParallelTask(2) as (tc1, tc2):
                    tc1.addTask("TaskMovie2Play", Movie2=self.newspaper.movie_Open, Wait=True)
                    tc2.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=NewspaperFade, Time=0.25 * 1000)  # speed fix
                    pass
                tc.addParam(self.object, "Open", True)

                tc.addTask("TaskSocketClick", Socket=self.newspaper.socket_Close)
                tc.addFunction(NewspaperManager.openNewspaper, self.NewspaperID)
                tc.addNotify(Notificator.onNewspaperShow, self.NewspaperID)
                tc.addParam(self.object, "Open", False)

                tc.addDisable(self.newspaper.socket_Close)
                tc.addTask("TaskInteractive", Object=self.newspaper.socket_Close, Value=False)
                tc.addTask("TaskNodeRemoveFromParent", Node=layerAttachGroupEntity)
                tc.addDisable(self.newspaper.movie_Open)

                tc.addEnable(self.newspaper.movie_Close)
                tc.addTask("TaskNodeAddChild", ParentNode=slotClose, ChildNode=layerAttachGroupEntity)

                with tc.addParallelTask(2) as (tc1, tc2):
                    tc1.addTask("TaskMovie2Play", Movie2=self.newspaper.movie_Close, Wait=True)
                    tc2.addTask("AliasFadeOut", FadeGroupName="FadeDialog", Time=0.25 * 1000, From=NewspaperFade)  # speed fix
                    pass

                tc.addTask("TaskNodeRemoveFromParent", Node=layerAttachGroupEntity)
                tc.addDisable("TaskEnable"self.newspaper.movie_Close)
                pass
            pass
        else:
            with TaskManager.createTaskChain(Name="NewspaperOpen", Cb=self._showComplete) as tc:
                tc.addEnable(self.newspaper.socket_Close)
                tc.addTask("TaskInteractive", Object=self.newspaper.socket_Close, Value=True)
                tc.addTask("TaskNodeAddChild", ParentNode=slotOpen, ChildNode=layerAttachGroupEntity)
                tc.addTask("TaskNodeEnable", Node=layerAttachGroupEntity, Value=True)
                tc.addNotify(Notificator.onNewspaperOpen, self.NewspaperID)

                with tc.addParallelTask(2) as (tc1, tc2):
                    tc1.addTask("TaskMovie2Play", Movie2=self.newspaper.movie_Open, Wait=True)
                    tc2.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=NewspaperFade, Time=0.25 * 1000)  # speed fix
                    pass
                tc.addParam(self.object, "Open", True)

                tc.addTask("TaskSocketClick", Socket=self.newspaper.socket_Close)
                tc.addFunction(NewspaperManager.openNewspaper, self.NewspaperID)
                tc.addNotify(Notificator.onNewspaperShow, self.NewspaperID)
                tc.addParam(self.object, "Open", False)

                tc.addDisable(self.newspaper.socket_Close)
                tc.addTask("TaskInteractive", Object=self.newspaper.socket_Close, Value=False)
                tc.addTask("TaskNodeRemoveFromParent", Node=layerAttachGroupEntity)
                tc.addDisable(self.newspaper.movie_Open)

                tc.addEnable(self.newspaper.movie_Close)
                tc.addTask("TaskNodeAddChild", ParentNode=slotClose, ChildNode=layerAttachGroupEntity)
                with tc.addParallelTask(2) as (tc1, tc2):
                    tc1.addTask("TaskMovie2Play", Movie2=self.newspaper.movie_Close, Wait=True)
                    tc2.addTask("AliasFadeOut", FadeGroupName="FadeDialog", Time=0.25 * 1000, From=NewspaperFade)  # speed fix
                    pass
                tc.addTask("TaskNodeRemoveFromParent", Node=layerAttachGroupEntity)
                tc.addDisable(self.newspaper.movie_Close)
                pass
            pass

        pass

    def _onActivate(self):
        GroupName = self.object.getGroupName()
        ObjectName = self.object.getName()

        if NewspaperManager.hasNewspaperID(GroupName, ObjectName) is False:
            Trace.log("Entity", 0, "Newspaper._onActivate not found NewspaperID %s:%s" % (GroupName, ObjectName))
            return
            pass

        newspaperID = NewspaperManager.getNewspaperID(GroupName, ObjectName)

        self.object.setNewspaperID(newspaperID)

        if TaskManager.existTaskChain(self.NewspaperID):
            TaskManager.cancelTaskChain(self.NewspaperID)
            pass

        self.newspaper = NewspaperManager.getNewspaper(self.NewspaperID)
        if self.ShowComplete is True and self.newspaper.repeat is False:
            return
            pass

        self.AttachLayerGroup = GroupManager.getGroup(self.newspaper.attachGroupName)
        self.__showNewspaper()
        pass

    def _showComplete(self, isSkip):
        if self.object is None or self.newspaper is None:
            return

        for group in self.tempEnableGroups:
            group.onDisable()
            pass

        self.tempEnableGroups = []

        self.object.setShowComplete(True)
        if self.newspaper.repeat is True:
            self.__showNewspaper()
            pass
        pass

    def _cleanData(self):
        if self.NewspaperID is None or self.newspaper is None:
            return

        if self.AttachLayerGroup is None:
            return

        if self.AttachLayerGroup.isActive() is False:
            return

        layerAttachGroupEntity = self.AttachLayerGroup.getEntity()
        layerAttachGroupEntity.removeFromParent()
        self.AttachLayerGroup = None
        #
        for group in self.tempEnableGroups:
            group.onDisable()
            pass

        self.newspaper.movie_Open.setEnable(False)
        self.newspaper.movie_Close.setEnable(False)
        self.newspaper = None
        #
        self.tempEnableGroups = []

        QuestManager.cancelQuest(self.Quest)
        self.Quest = None
        pass

    def _onDeactivate(self):
        if TaskManager.existTaskChain("Newspaper%s" % (self.NewspaperID)):
            TaskManager.cancelTaskChain("Newspaper%s" % (self.NewspaperID))
            pass

        if TaskManager.existTaskChain("NewspaperOpen%s" % (self.NewspaperID)):
            TaskManager.cancelTaskChain("NewspaperOpen%s" % (self.NewspaperID))
            pass

        self._cleanData()
        pass

    pass
