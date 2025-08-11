from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

from NotebookManager import NotebookManager

class Notebook(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "PageSize")
        Type.addAction(Type, "OpenNotes")
        Type.addAction(Type, "CloseNotes")
        Type.addActionActivate(Type, "CurrentNote")
        Type.addActionActivate(Type, "CurrentPageID", Update=Notebook.__updateCurrentPageID)

        pass

    def __init__(self):
        super(Notebook, self).__init__()
        self.noteMovies = {}
        self.garbage = {}
        self.socket = {}
        self.currentActivateMovie = None
        pass

    def __updateCurrentPageID(self, value):
        self.__setupCurrentPage(value)
        pass

    def __setupCurrentPage(self, value):
        self.destroyPreviousPage()
        openNotes = self.OpenNotes
        closeNotes = self.CloseNotes
        beginIndex = value * self.PageSize
        endIndex = beginIndex + self.PageSize
        currentPageNotes = openNotes[beginIndex:endIndex]
        for i, noteID in enumerate(currentPageNotes):
            noteEntry = NotebookManager.getEntry(i)
            self.noteMovies[noteID] = noteEntry
            if noteID not in closeNotes:
                noteMovie = noteEntry.getOpenMovie()
                pass
            else:
                noteMovie = noteEntry.getCloseMovie()
                pass
            self.__setupMovie(noteMovie, noteID)
            pass
        if self.CurrentNote in currentPageNotes:
            self.selectMovie(self.CurrentNote)
            pass
        self.__updateButtons()
        pass

    def destroyPreviousPage(self):
        self.destroyTextes()
        for key, entries in self.noteMovies.iteritems():
            openMovie = entries.getOpenMovie()
            openMovie.setEnable(False)
            closeMovie = entries.getCloseMovie()
            closeMovie.setEnable(False)
            selectOpenMovie = entries.getSelectOpenMovie()
            selectOpenMovie.setEnable(False)
            selectCloseMovie = entries.getSelectCloseMovie()
            selectCloseMovie.setEnable(False)
            pass
        self.noteMovies.clear()
        pass

    def disableAllMovies(self):
        allEntries = NotebookManager.getAllEntries()
        for key, entries in allEntries.iteritems():
            openMovie = entries.getOpenMovie()
            openMovie.setEnable(False)
            closeMovie = entries.getCloseMovie()
            closeMovie.setEnable(False)
            selectOpenMovie = entries.getSelectOpenMovie()
            selectOpenMovie.setEnable(False)
            selectCloseMovie = entries.getSelectCloseMovie()
            selectCloseMovie.setEnable(False)
            pass
        pass

    def _onPreparation(self):
        super(Notebook, self)._onPreparation()
        self.disableAllMovies()
        pass

    def _onActivate(self):
        super(Notebook, self)._onActivate()

        if TaskManager.existTaskChain("NotebookPagesLeft"):
            TaskManager.cancelTaskChain("NotebookPagesLeft")
            pass
        if TaskManager.existTaskChain("NotebookPagesRight"):
            TaskManager.cancelTaskChain("NotebookPagesRight")
            pass

        self.Button_Left = self.object.getObject("Button_Left")
        self.Button_Right = self.object.getObject("Button_Right")

        with TaskManager.createTaskChain(Name="NotebookPagesLeft", Repeat=True) as tc:
            tc.addTask("TaskButtonClick", Button=self.Button_Left, AutoEnable=False)
            tc.addFunction(self.__changePage, -1)
            pass

        with TaskManager.createTaskChain(Name="NotebookPagesRight", Repeat=True) as tc:
            tc.addTask("TaskButtonClick", Button=self.Button_Right, AutoEnable=False)
            tc.addFunction(self.__changePage, 1)
            pass
        pass

    def __changePage(self, value):
        oldIndex = self.CurrentPageID
        newIndex = oldIndex + value
        if newIndex < 0:
            newIndex = 0
            pass
        beginIndex = self.CurrentPageID * self.PageSize
        endIndex = beginIndex + self.PageSize
        currentPageNotes = self.OpenNotes[beginIndex:endIndex]
        if len(currentPageNotes) == 0:
            newIndex = oldIndex
            pass
        self.object.setParam("CurrentPageID", newIndex)
        pass

    def __updateButtons(self):
        if self.CurrentPageID > 0:
            self.Button_Left.setParam("Interactive", 1)
            pass
        elif self.CurrentPageID == 0:
            self.Button_Left.setParam("Interactive", 0)
            pass
        beginIndex = (self.CurrentPageID + 1) * self.PageSize
        endIndex = beginIndex + self.PageSize
        currentPageNotes = self.OpenNotes[beginIndex:endIndex]
        if len(currentPageNotes) == 0:
            self.Button_Right.setParam("Interactive", 0)
            pass
        else:
            self.Button_Right.setParam("Interactive", 1)
            pass
        pass

    def _onMouseButtonEvent(self, context, event, hs):
        if hs not in self.socket.keys():
            return True
        if event.button != 0:
            return True
        if event.isDown is True:
            self.clickHandler(hs)
            return True
        return True

    def __setupMovie(self, movie, noteId):
        textID = NotebookManager.getNote(noteId)
        movie.setEnable(True)
        noteMovieEn = movie.getEntity()
        movieSlot = noteMovieEn.getMovieSlot("text")
        Text = Mengine.createNode("TextField")
        Text.enable()
        Text.setTextId(textID)
        movieSlot.addChild(Text)

        sc = "socket"
        if noteMovieEn.hasSocket(sc) is True:
            socket = noteMovieEn.getSocket(sc)
            socket.setEventListener(onHandleMouseButtonEvent=Function(self._onMouseButtonEvent, socket))
            self.socket[socket] = noteId
            pass
        self.garbage[movie] = Text
        pass

    def disableMovie(self, movie):
        if movie in self.garbage:
            text = self.garbage[movie]
            text.removeFromParent()
        movie.setEnable(False)
        pass

    def selectMovie(self, noteId):
        if noteId not in self.noteMovies:
            return
            pass
        if self.currentActivateMovie is not None:
            self.disableMovie(self.currentActivateMovie)
            self.currentActivateMovie = None
            pass

        entry = self.noteMovies[noteId]
        if noteId not in self.object.getCloseNotes():
            newMovie = entry.getSelectOpenMovie()
            if newMovie is None:
                return
                pass
            oldMovie = entry.getOpenMovie()
            self.disableMovie(oldMovie)
            pass
        else:
            newMovie = entry.getSelectCloseMovie()
            if newMovie is None:
                return
                pass
            oldMovie = entry.getCloseMovie()
            self.disableMovie(oldMovie)
            pass
        self.__setupMovie(newMovie, noteId)
        self.currentActivateMovie = newMovie
        pass

    def clickHandler(self, hs):
        noteId = self.socket[hs]
        self.disableCurrentActivateMovie()
        self.object.setParam("CurrentNote", noteId)
        self.selectMovie(noteId)
        Notification.notify(Notificator.onNoteClick, noteId)
        pass

    def disableCurrentActivateMovie(self):
        noteId = self.CurrentNote
        if noteId not in self.noteMovies:
            return
            pass
        entry = self.noteMovies[noteId]
        if noteId not in self.object.getCloseNotes():
            newMovie = entry.getOpenMovie()
            if newMovie is None:
                return
                pass
            oldMovie = entry.getSelectOpenMovie()
            self.disableMovie(oldMovie)
            pass
        else:
            newMovie = entry.getCloseMovie()
            if newMovie is None:
                return
                pass
            oldMovie = entry.getSelectCloseMovie()
            self.disableMovie(oldMovie)
            pass
        self.__setupMovie(newMovie, noteId)
        pass

    def destroyTextes(self):
        for text in self.garbage.itervalues():
            text.removeFromParent()
            pass
        self.garbage.clear()
        pass

    def _onPreparationDeactivate(self):
        super(Notebook, self)._onPreparationDeactivate()
        self.destroyTextes()
        pass

    def _onDeactivate(self):
        super(Notebook, self)._onDeactivate()
        if TaskManager.existTaskChain("NotebookPagesLeft"):
            TaskManager.cancelTaskChain("NotebookPagesLeft")
            pass
        if TaskManager.existTaskChain("NotebookPagesRight"):
            TaskManager.cancelTaskChain("NotebookPagesRight")
            pass
        pass

    pass
