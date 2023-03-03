from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager

from HOPA.BonusManager import BonusManager
from HOPA.WallPaperManager import WallPaperManager


class BonusPapers(BaseEntity):
    def __init__(self):
        super(BonusPapers, self).__init__()
        self.buttons_cbs = {}
        self.wallpapers = []
        self.current_ind = 0

        # POP UP - OPTION - ADD Movie2_PlatePopupPaperSave TO ENABLE QUESTION FEATURE
        self.popup_save_paper = None
        self.popup_save_paper_entity_node = None
        self.popup_save_paper_button_yes = None
        self.popup_save_paper_button_cancel = None

    def _onPreparation(self):
        switch_buttons = BonusManager.getStates()
        for button in switch_buttons.values():
            GroupManager.getObject('Bonus', button.button_name).setBlock(False)

        button_papers = GroupManager.getObject('Bonus', 'Movie2Button_BonusPapers')
        button_papers.setBlock(True)

        self.next_paper_button = self.object.getObject('Movie2Button_NextPaper')
        self.pre_paper_button = self.object.getObject('Movie2Button_PrePaper')
        self.set_paper_button = self.object.getObject('Movie2Button_SetPaper')

        self._setupPopUpQuestion()

        self.buttons_cbs = {
            self.next_paper_button: self.__cbScopeNextButtonClick,
            self.pre_paper_button: self.__cbScopePreButtonClick,
            self.set_paper_button: self.__cbScopeSetButtonClick
        }

        for wallpaper in WallPaperManager.getWallpapers():
            wallpaper_movie = self.object.getObject(wallpaper.movie_name)
            wallpaper_movie.setEnable(wallpaper.status)

            if wallpaper.status is True:
                self.current_ind = len(self.wallpapers)

            self.wallpapers.append(wallpaper_movie)

    def _setupPopUpQuestion(self):
        if self.object.hasObject("Movie2_PlatePopupPaperSave") is False:
            return

        if any([self.object.hasObject("Movie2Button_PopupPaperSaveYes") is False,
                self.object.hasObject("Movie2Button_PopupPaperSaveCancel") is False]):
            if _DEVELOPMENT is True:
                Trace.msg_err("You add pop up window, but where is buttons? "
                              "Missing Movie2Button_PopupPaperSaveYes or Movie2Button_PopupPaperSaveCancel")
            return

        self.popup_save_paper_button_yes = self.object.getObject('Movie2Button_PopupPaperSaveYes')
        self.popup_save_paper_button_cancel = self.object.getObject('Movie2Button_PopupPaperSaveCancel')

        self.popup_save_paper = self.object.getObject('Movie2_PlatePopupPaperSave')
        self.popup_save_paper_entity_node = self.popup_save_paper.getEntityNode()
        popup_save_paper_slot_yes = self.popup_save_paper.getMovieSlot('button_yes')
        popup_save_paper_slot_cancel = self.popup_save_paper.getMovieSlot('button_cancel')

        if self.popup_save_paper_button_yes is not None:
            popup_save_paper_slot_yes.addChild(self.popup_save_paper_button_yes.getEntityNode())
        if self.popup_save_paper_button_cancel is not None:
            popup_save_paper_slot_cancel.addChild(self.popup_save_paper_button_cancel.getEntityNode())

        object_entity_node = self.object.getEntityNode()
        object_entity_node.addChild(self.popup_save_paper_entity_node)

        self.popup_save_paper.setEnable(False)

    def _onActivate(self):
        self._runTaskChain()

    def _onDeactivate(self):
        self.__cleanUp()

    def __setWallPaperStatus(self, wallpaper_movie, status):
        index = self.wallpapers.index(wallpaper_movie)
        wallpaper = WallPaperManager.getWallpaperByIndex(index)
        wallpaper.status = status

    def _scopeChangeWallPaper(self, source, old_wp, new_wp):
        with source.addParallelTask(2) as (source_old, source_new):
            source_old.addTask("AliasObjectAlphaTo", Object=old_wp, Time=1000, From=1.0, To=0.0, Wait=True)
            source_old.addDisable(old_wp)
            source_old.addFunction(self.__setWallPaperStatus, old_wp, False)

            source_new.addEnable(new_wp)
            source_new.addTask("AliasObjectAlphaTo", Object=new_wp, Time=1000, From=0.0, To=1.0, Wait=True)
            source_new.addFunction(self.__setWallPaperStatus, new_wp, True)

    def __cbScopeNextButtonClick(self, source):
        source.addScope(self.__scopeSwitchButtonClick, 1)

    def __cbScopePreButtonClick(self, source):
        source.addScope(self.__scopeSwitchButtonClick, -1)

    def __scopeSwitchButtonClick(self, source, value):
        current_wp = self.wallpapers[self.current_ind]
        index_new_wp = (self.current_ind + value) % len(self.wallpapers)
        new_wp = self.wallpapers[index_new_wp]

        self.current_ind = index_new_wp

        source.addScope(self._scopeChangeWallPaper, current_wp, new_wp)

    def __cbScopeSetButtonClick(self, source):
        if self.popup_save_paper is None:
            # DEFAULT WITHOUT QUESTION
            source.addScope(self.__scopeSetWallpaper)
            return  # ----------------

        # AT FIRST ASK PLAYER - IF TRUE SET WALLPAPER
        source.addEnable(self.popup_save_paper)

        with source.addRaceTask(2) as (source_yes, source_cancel):
            source_yes.addTask('TaskMovie2ButtonClick', Movie2Button=self.popup_save_paper_button_yes)
            source_yes.addScope(self.__scopeSetWallpaper)
            source_cancel.addTask('TaskMovie2ButtonClick', Movie2Button=self.popup_save_paper_button_cancel)

        source.addDisable(self.popup_save_paper)

    def __scopeSetWallpaper(self, source):
        current_wallpaper = WallPaperManager.getWallpapers()[self.current_ind]

        source.addFunction(Mengine.copyUserPicture, current_wallpaper.resource_name,
                           r'{}.jpg'.format(current_wallpaper.resource_name))

        source.addFunction(Mengine.updateUserWallpaper, r'{}.jpg'.format(current_wallpaper.resource_name))

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            for (button, __cb), race_button_click in tc.addRaceTaskList(self.buttons_cbs.iteritems()):
                race_button_click.addTask('TaskMovie2ButtonClick', Movie2Button=button)
                race_button_click.addScope(__cb)

    def __cleanUp(self):
        if self.tc:
            self.tc.cancel()
        self.tc = None

        self.buttons_cbs = {}
        self.wallpapers = []
        self.current_ind = 0
