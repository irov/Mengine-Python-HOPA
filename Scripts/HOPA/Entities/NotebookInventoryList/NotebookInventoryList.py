from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager

from NotebookInventoryListManager import NotebookInventoryListManager


SLOT_NAME = "text0"
TEXT_ALIAS_NAME = "$text0"
ID_EMPTY_TEXT = "ID_EMPTY_TEXT"


class NotebookInventoryList(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "OpenNotes")

    def __init__(self):
        super(NotebookInventoryList, self).__init__()
        self.button = None
        self.isClick = True
        self.openNotes = []
        self.movieTexts = {}
        self.Movies = {}
        self.tc = None

    def __disableAll(self):
        allEntries = NotebookInventoryListManager.getAllShowEntry()
        for entry in allEntries.values():
            show = entry.getShowMovie()
            show.setEnable(False)

            if show.entity.hasMovieText(TEXT_ALIAS_NAME):
                show.setTextAliasEnvironment(show.name)
                Mengine.setTextAlias(show.name, TEXT_ALIAS_NAME, ID_EMPTY_TEXT)

            idle = entry.getIdleMovie()
            idle.setEnable(False)

            if idle.entity.hasMovieText(TEXT_ALIAS_NAME):
                idle.setTextAliasEnvironment(idle.name)
                Mengine.setTextAlias(idle.name, TEXT_ALIAS_NAME, ID_EMPTY_TEXT)

            hide = entry.getHideMovie()
            hide.setEnable(False)

            if hide.entity.hasMovieText(TEXT_ALIAS_NAME):
                hide.setTextAliasEnvironment(hide.name)
                Mengine.setTextAlias(hide.name, TEXT_ALIAS_NAME, ID_EMPTY_TEXT)

    def _onPreparation(self):
        super(NotebookInventoryList, self)._onPreparation()
        self.__disableAll()

    def prepareTextFields(self, movieLocalID):
        textField = Mengine.createNode("TextField")
        textField.setVerticalCenterAlign()
        textField.setHorizontalCenterAlign()
        textField.enable()
        noteID = self.openNotes[movieLocalID]
        TextID = NotebookInventoryListManager.getText(noteID)
        textField.setTextId(TextID)
        self.movieTexts[movieLocalID] = textField

    def prepareTasksMovie(self, movie, movieLocalID):
        movie.setEnable(True)

        movieEntity = movie.getEntity()
        entNode = movie.getEntityNode()

        scene = SceneManager.getCurrentScene()
        if scene is None:
            return

        if scene.hasSlot("Notebook"):
            layer = scene.getSlot("Notebook")
        else:
            layer = scene.getMainLayer()

        if layer is None:
            return
        layer.addChild(entNode)

        noteID = self.openNotes[movieLocalID]
        TextID = NotebookInventoryListManager.getText(noteID)

        # case when we use text alias
        # this is new correct way to set text
        if movieEntity.hasMovieText(TEXT_ALIAS_NAME):
            Mengine.setTextAlias(movie.name, TEXT_ALIAS_NAME, TextID)

        # case when we use slot where will be created textNode in code
        # where this one method is deprecated
        # it's do not allow as to scale text in box
        elif movieEntity.hasMovieSlot(SLOT_NAME):
            movieSlot = movieEntity.getMovieSlot(SLOT_NAME)
            textField = self.movieTexts[movieLocalID]
            movieSlot.addChild(textField)

        else:
            msg = "NotebookInventoryList: movie \"%s\" should has slot \"%s\" or text alias: \"%s\"" % (movie.name, SLOT_NAME, TEXT_ALIAS_NAME)
            Trace.log("Entity", 0, msg)
            return

        movie.setEnable(False)

    def finaliseTasksMovie(self, movie, movieLocalID):
        movieEntity = movie.getEntity()
        movieEntity.removeFromParent()
        movie.setEnable(False)

    def cleanNodes(self):
        for key in self.movieTexts:
            textField = self.movieTexts[key]
            if textField is not None:
                Mengine.destroyNode(textField)
            self.movieTexts[key] = None

        for movieStatesList in self.Movies.itervalues():
            for movieState in movieStatesList:
                movieEntity = movieState.getEntity()
                movieEntity.removeFromParent()
                movieState.setEnable(False)

    def setCurrentPlayingMovie(self, movie):
        self.currentPlayingMovie = movie

    def playMovies(self, scope, movie):
        scope.addTask("TaskMovie2Play", Movie2=movie, Wait=True)

    def __tasksPlay(self, scope):
        StairsDelay = 500.0

        self.Movies = {}
        self.movieTexts = {}
        movieQueue = []

        openNotesLen = len(self.openNotes)
        if openNotesLen == 0:
            return

        for movieLocalID in range(openNotesLen):
            Movie = NotebookInventoryListManager.getShowEntry(movieLocalID + 1)
            if Movie is None:
                return

            movieShow = Movie.getShowMovie()
            movieHide = Movie.getHideMovie()
            movieIdle = Movie.getIdleMovie()
            self.Movies[movieLocalID] = [movieShow, movieIdle, movieHide]

            self.prepareTextFields(movieLocalID)

            movieQueue.append(movieLocalID)

        for movieLocalID, parallel in scope.addParallelTaskList(movieQueue):
            # [0] - movieShow
            parallel.addFunction(self.prepareTasksMovie, self.Movies[movieLocalID][0], movieLocalID)
            parallel.addDelay(3.0 + StairsDelay * movieLocalID)
            parallel.addTask("TaskEnable", Object=self.Movies[movieLocalID][0], Value=True)
            parallel.addScope(self.playMovies, self.Movies[movieLocalID][0])
            parallel.addTask("TaskMovie2Rewind", Movie2=self.Movies[movieLocalID][0])
            parallel.addFunction(self.finaliseTasksMovie, self.Movies[movieLocalID][0], movieLocalID)
            # [1] - movieIdle
            parallel.addFunction(self.prepareTasksMovie, self.Movies[movieLocalID][1], movieLocalID)
            parallel.addTask("TaskEnable", Object=self.Movies[movieLocalID][1], Value=True)
            parallel.addScope(self.playMovies, self.Movies[movieLocalID][1])
            parallel.addDelay(self.delay)
            parallel.addTask("TaskMovie2Rewind", Movie2=self.Movies[movieLocalID][1])
            parallel.addFunction(self.finaliseTasksMovie, self.Movies[movieLocalID][1], movieLocalID)
            # [2] - movieHide
            parallel.addFunction(self.prepareTasksMovie, self.Movies[movieLocalID][2], movieLocalID)
            parallel.addTask("TaskEnable", Object=self.Movies[movieLocalID][2], Value=True)
            parallel.addScope(self.playMovies, self.Movies[movieLocalID][2])
            parallel.addTask("TaskMovie2Rewind", Movie2=self.Movies[movieLocalID][2])
            parallel.addFunction(self.finaliseTasksMovie, self.Movies[movieLocalID][2], movieLocalID)

        scope.addFunction(self.cleanNodes)

    def checkValidate(self):
        trigerData = NotebookInventoryListManager.getTriggerData()
        groupName = trigerData.getGroupName()

        hasOpenTabDiaryScene = SceneManager.hasLayerScene(groupName)
        if hasOpenTabDiaryScene is False:
            return False

        if TaskManager.existTaskChain("NotesRound"):
            return False

        return True

    def __waitEnter(self, scope):
        openNotes = self.object.getOpenNotes()
        self.openNotes = openNotes[:]
        openNotesLen = len(openNotes)

        scope.addTask("TaskSceneInit", SceneAny=True)
        if openNotesLen == 0:
            scope.addTask("TaskListener", ID=Notificator.onTasksOpen)

        scope.addScope(self.__tasksPlay)

    def runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Name="NotebookInventoryList", Repeat=True)
        with self.tc as tc:
            tc.addTask('TaskMovie2ButtonClick', Movie2Button=self.Trigger)
            with tc.addIfTask(self.checkValidate) as (true_source, false_source):
                true_source.addScope(self.__waitEnter)

    def _onActivate(self):
        trigerData = NotebookInventoryListManager.getTriggerData()
        groupName = trigerData.getGroupName()
        objectName = trigerData.getObjectName()
        self.isClick = trigerData.getIsClick()
        self.ClickOnButton = trigerData.getClickOnButton()
        self.AutoEnable = trigerData.getAutoEnable()
        self.Trigger = GroupManager.getObject(groupName, objectName)
        self.delay = DefaultManager.getDefaultFloat("TasksShowDelay", 3.0)
        self.delay *= 1000  # speed fix
        self.enterDelay = DefaultManager.getDefaultFloat("EnterTaskShowDelay", 0.5)
        self.enterDelay *= 1000  # speed fix
        self.runTaskChain()

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.cleanNodes()
