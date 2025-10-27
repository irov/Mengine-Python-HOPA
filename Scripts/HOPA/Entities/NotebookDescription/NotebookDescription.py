from Foundation.Entity.BaseEntity import BaseEntity
from NotebookDescriptionManager import NotebookDescriptionManager


class NotebookDescription(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate("CurrentNote", Update=NotebookDescription._updateCurrentNote)
        pass

    def __init__(self):
        super(NotebookDescription, self).__init__()
        self.MovieDescription = None
        self.Text = None
        pass

    def _updateCurrentNote(self, NoteID):
        if NoteID is None:
            return
            pass
        self.openDescription(NoteID)
        pass

    def openDescription(self, NoteID):
        if self.Text is not None:
            self.Text.removeFromParent()
            Mengine.destroyNode(self.Text)
            self.Text = None
            pass
        if self.MovieDescription is not None:
            self.MovieDescription.setEnable(False)
            pass

        description = NotebookDescriptionManager.getDescription(NoteID)
        textID = description.getTextID()
        movie = description.getMovie()
        movie.setEnable(True)
        movieEntity = movie.getEntity()

        movieSlot = movieEntity.getMovieSlot("text")
        self.Text = Mengine.createNode("TextField")
        self.Text.enable()

        self.Text.setTextId(textID)
        movieSlot.addChild(self.Text)

        self.MovieDescription = movie
        pass

    def __disableAll(self):
        allEntries = NotebookDescriptionManager.getAllDescriptions()
        for key, entry in allEntries.iteritems():
            movie = entry.getMovie()
            movie.setEnable(False)
            pass

    def _onPreparation(self):
        super(NotebookDescription, self)._onPreparation()
        self.__disableAll()
        pass

    def _onActivate(self):
        pass

    def _onDeactivate(self):
        if self.Text is not None:
            self.Text.removeFromParent()
            # Mengine.destroyNode(self.Text)
            self.Text = None
