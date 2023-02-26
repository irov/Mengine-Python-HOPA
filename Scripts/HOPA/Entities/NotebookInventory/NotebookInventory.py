import Trace
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager

from NotebookInventoryManager import NotebookInventoryManager

SLOT_NAME = "text"
TEXT_ALIAS_NAME = "$text"
ID_EMPTY_TEXT = "ID_EMPTY_TEXT"

class NotebookInventory(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "OpenNotes", Append=NotebookInventory._appendOpenNotes)
        Type.addAction(Type, "CloseNotes", Append=NotebookInventory._appendCloseNotes)

    def __init__(self):
        super(NotebookInventory, self).__init__()
        self.noteRound = []
        self.textField = None

    def __disableAll(self):
        all_entries = NotebookInventoryManager.getAllActivateEntries()

        for entry in all_entries.values():
            open_ = entry.getOpenMovie()
            open_.setEnable(False)

            if open_.entity.hasMovieText(TEXT_ALIAS_NAME):
                open_.setTextAliasEnvironment(open_.name)
                Mengine.setTextAlias(open_.name, TEXT_ALIAS_NAME, ID_EMPTY_TEXT)

            close = entry.getCloseMovie()
            close.setEnable(False)

            if close.entity.hasMovieText(TEXT_ALIAS_NAME):
                close.setTextAliasEnvironment(close.name)
                Mengine.setTextAlias(close.name, TEXT_ALIAS_NAME, ID_EMPTY_TEXT)

    def _onPreparation(self):
        super(NotebookInventory, self)._onPreparation()
        self.__disableAll()

    def _onActivate(self):
        super(NotebookInventory, self)._onActivate()

    def _onDeactivate(self):
        super(NotebookInventory, self)._onDeactivate()

        self.__checkTasks()
        self.currentMovie = None

    def _appendOpenNotes(self, id_, value):
        self.noteRound.append(value)

        self.__checkValidate()

    def _appendCloseNotes(self, id_, value):
        self.noteRound.append(value)

        self.__checkValidate()

    def __checkValidate(self):
        if len(self.noteRound) == 0:
            return

        if TaskManager.existTaskChain("NotesRound") is True:
            return

        current_scene_name = SceneManager.getCurrentSceneName()

        if current_scene_name is None:
            return

        if SceneManager.isCurrentSceneActive() is False:
            return

        description = SceneManager.getCurrentDescription()
        description_name = description.getName()
        if description_name != "Main":
            return

        next_id = self.noteRound[0]

        if next_id in self.object.getParam("CloseNotes"):
            self.__startNoteClose(next_id)

        else:
            self.__startNoteOpen(next_id)

    def __startNoteOpen(self, note_id):
        self.noteRound.remove(note_id)
        activate_entry = NotebookInventoryManager.getActivateEntry(note_id)

        activate_movie = activate_entry.getOpenMovie()
        if activate_movie is None:
            return

        activate_movie.setEnable(True)
        self.currentMovie = activate_movie
        entity = activate_movie.getEntity()

        entity.movie.compile()

        text_id = activate_entry.getOpenTextID()

        # case when we use text alias
        # this is new correct way to set text
        if entity.hasMovieText(TEXT_ALIAS_NAME):
            Mengine.setTextAlias(activate_movie.name, TEXT_ALIAS_NAME, text_id)

        # case when we use slot where will be created textNode in code
        # where this one method is deprecated
        # it's do not allow as to scale text in box
        elif entity.hasMovieSlot("text"):
            slot_text = entity.getMovieSlot("text")

            self.textField = Mengine.createNode("TextField")
            self.textField.setVerticalCenterAlign()
            self.textField.setHorizontalCenterAlign()

            self.textField.setTextID(text_id)
            self.textField.enable()
            slot_text.addChild(self.textField)

        else:
            msg = "NotebookInventoryList: movie \"%s\" should has slot \"%s\" or text alias: \"%s\"" % (activate_movie.name, SLOT_NAME, TEXT_ALIAS_NAME)
            Trace.log("Entity", 0, msg)
            return

        with TaskManager.createTaskChain(Name="NotesRound", Cb=self.__removeRoundTasks) as tc:
            tc.addTask("TaskMoviePlay", Movie=activate_movie, Wait=True)

    def __startNoteClose(self, noteID):
        self.noteRound.remove(noteID)
        activate_entry = NotebookInventoryManager.getActivateEntry(noteID)

        activate_movie = activate_entry.getCloseMovie()

        if activate_movie is None:
            return

        activate_movie.setEnable(True)

        self.currentMovie = activate_movie

        entity = activate_movie.getEntity()
        entity.movie.compile()

        text_id = activate_entry.getCloseTextID()

        # case when we use text alias
        if entity.hasMovieText(TEXT_ALIAS_NAME):
            Mengine.setTextAlias(activate_movie.name, TEXT_ALIAS_NAME, text_id)

        # case when we use slot where will be created textNode in code
        elif entity.hasMovieSlot("text"):
            self.textField = Mengine.createNode("TextField")
            self.textField.setVerticalCenterAlign()
            self.textField.setHorizontalCenterAlign()

            self.textField.setTextID(text_id)
            self.textField.enable()

            slot_text = entity.getMovieSlot("text")
            slot_text.addChild(self.textField)

        else:
            msg = "NotebookInventoryList: movie \"%s\" should has slot \"%s\" or text alias: \"%s\"" % (activate_movie.name, SLOT_NAME, TEXT_ALIAS_NAME)
            Trace.log("Entity", 0, msg)
            return

        with TaskManager.createTaskChain(Name="NotesRound", Cb=self.__removeRoundTasks) as tc:
            tc.addTask("TaskMoviePlay", Movie=activate_movie, Wait=True)

    def __removeRoundTasks(self, is_skip):
        if self.textField is not None:
            self.textField.removeFromParent()
            Mengine.destroyNode(self.textField)
            self.textField = None

        if self.currentMovie is not None:
            self.currentMovie.setEnable(False)
        self.__checkTasks()
        self.__checkValidate()

    def __checkTasks(self):
        if TaskManager.existTaskChain("NotesRound") is True:
            TaskManager.cancelTaskChain("NotesRound")