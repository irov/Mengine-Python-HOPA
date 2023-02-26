from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.SurveyPhotoGalleryManager import SurveyPhotoGalleryManager

BUTTON_CLOSE_NAME = "Movie2Button_Frame"
SOCKET_BACK_NAME = "back"

class SurveyPhotoGallery(BaseEntity):
    def __init__(self):
        super(SurveyPhotoGallery, self).__init__()

        self.tc = None

    def _onInitialize(self, *args, **kwargs):
        super(SurveyPhotoGallery, self)._onInitialize(*args, **kwargs)

        group = self.object.getGroup()

        self.show_time = DefaultManager.getDefaultFloat("SurveyPhotoShowTime", 200.0)
        self.hide_time = DefaultManager.getDefaultFloat("SurveyPhotoHideTime", 200.0)

        self.fade_on = DefaultManager.getDefaultFloat("SurveyFadeValue", 0.5)
        self.fade_off = 0.0

        self.scale_on = (1.0, 1.0, 1.0)
        self.scale_off = (0.2, 0.2, 0.2)

        self.alpha_on = 1.0
        self.alpha_off = 0.0

        self.btn_close_photo = group.getObject(BUTTON_CLOSE_NAME)
        self.btn_close_photo.setEnable(False)

        ''' Disable Zoomed In Photos on Start '''
        for photo in SurveyPhotoGalleryManager.s_photos.values():
            photo.setEnable(False)

    def _onActivate(self):
        super(SurveyPhotoGallery, self)._onActivate()
        # print "SurveyPhotoGallery._onActivate"

        self.tc = TaskManager.createTaskChain(Repeat=True)

        buttons = SurveyPhotoGalleryManager.getButtons()
        # print "SurveyPhotoGallery buttons", buttons

        click_holder = Holder()
        with self.tc as tc:
            for button, tc_race in tc.addRaceTaskList(buttons):
                tc_race.addTask("TaskMovie2ButtonClick", Movie2Button=button)
                tc_race.addFunction(click_holder.set, button)

            tc.addScope(self.scopeResolveClick, click_holder)

    def scopeResolveClick(self, source, holder):
        button = holder.get()
        # source.addPrint("You clicked on {}".format(button.getName()))

        source.addNotify(Notificator.onSurveyPhotoOpen)

        with source.addParallelTask(3) as (source_fade, source_photo, source_btn):
            source_fade.addScope(self.scopeFadeIn)
            source_photo.addScope(self.scopeShowPhoto, button)
            source_btn.addScope(self.scopeShowButtonClose, button)

        with source.addRaceTask(2) as (source_socket, source_btn):
            source_socket.addScope(self.scopeClickBackSocket, button)
            source_btn.addScope(self.scopeClickCloseButton)

        source.addNotify(Notificator.onSurveyPhotoClose)

        with source.addParallelTask(3) as (source_fade, source_photo, source_btn):
            source_fade.addScope(self.scopeFadeOut)
            source_photo.addScope(self.scopeHidePhoto, button)
            source_btn.addScope(self.scopeHideButtonClose, button)

    def getContentCenter(self):
        resolution = Mengine.getContentResolution()

        content_width = resolution.getWidth()
        content_height = resolution.getHeight()

        content_center = (content_width / 2, content_height / 2)

        return content_center

    def scopeZoomOutObject(self, source, object_, from_position, to_position):
        content_center = self.getContentCenter()

        entity_node = object_.getEntityNode()
        entity_node.setOrigin(content_center)

        with source.addParallelTask(3) as (source_alpha, source_move, source_scale):
            source_alpha.addTask("TaskNodeAlphaTo", Node=entity_node, From=self.alpha_off, To=self.alpha_on, Time=self.show_time)
            source_move.addTask("TaskNodeMoveTo", Node=entity_node, From=from_position, To=to_position, Time=self.show_time)
            source_scale.addTask("TaskNodeScaleTo", Node=entity_node, From=self.scale_off, To=self.scale_on, Time=self.show_time)

    def scopeZoomInObject(self, source, object_, from_position, to_position):
        content_center = self.getContentCenter()

        entity_node = object_.getEntityNode()
        entity_node.setOrigin(content_center)

        with source.addParallelTask(3) as (source_alpha, source_move, source_scale):
            source_alpha.addTask("TaskNodeAlphaTo", Node=entity_node, From=self.alpha_on, To=self.alpha_off, Time=self.show_time)
            source_move.addTask("TaskNodeMoveTo", Node=entity_node, From=from_position, To=to_position, Time=self.show_time)
            source_scale.addTask("TaskNodeScaleTo", Node=entity_node, From=self.scale_on, To=self.scale_off, Time=self.show_time)

    def scopeZoomOutObjectFromButton(self, source, object_, button):
        button_center = button.getCurrentMovieSocketCenter()
        content_center = self.getContentCenter()

        source.addScope(self.scopeZoomOutObject, object_, button_center, content_center)

    def scopeZoomInObjectToButton(self, source, object_, button):
        button_center = button.getCurrentMovieSocketCenter()
        content_center = self.getContentCenter()

        source.addScope(self.scopeZoomInObject, object_, content_center, button_center)

    def scopeClickBackSocket(self, source, button):
        photo = SurveyPhotoGalleryManager.getPhoto(button)

        source.addTask("TaskMovie2SocketClick", Movie2=photo, SocketName=SOCKET_BACK_NAME)

    def scopeClickCloseButton(self, source):
        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.btn_close_photo)

    def scopeFadeIn(self, source):
        group_name = self.object.getGroupName()
        source.addTask("AliasFadeIn", FadeGroupName=group_name, To=self.fade_on, Time=self.show_time)

    def scopeFadeOut(self, source):
        group_name = self.object.getGroupName()
        source.addTask("AliasFadeOut", FadeGroupName=group_name, From=self.fade_on, To=self.fade_off, Time=self.hide_time)

    def scopeShowPhoto(self, source, button):
        photo = SurveyPhotoGalleryManager.getPhoto(button)

        source.addEnable(photo)
        source.addScope(self.scopeZoomOutObjectFromButton, photo, button)

        # source.addTask("AliasObjectAlphaTo",  #                Object=photo, From=self.alpha_off, To=self.alpha_on, Time=self.show_time)

    def scopeHidePhoto(self, source, button):
        photo = SurveyPhotoGalleryManager.getPhoto(button)

        # source.addTask("AliasObjectAlphaTo",
        #                Object=photo, From=self.alpha_on, To=self.alpha_off, Time=self.hide_time)

        source.addScope(self.scopeZoomInObjectToButton, photo, button)
        source.addDisable(photo)

    def scopeShowButtonClose(self, source, button):
        source.addEnable(self.btn_close_photo)

        source.addScope(self.scopeZoomOutObjectFromButton, self.btn_close_photo, button)

        # source.addTask("AliasObjectAlphaTo",  #                Object=self.btn_close_photo, From=self.alpha_off, To=self.alpha_on, Time=self.show_time)

    def scopeHideButtonClose(self, source, button):
        source.addScope(self.scopeZoomInObjectToButton, self.btn_close_photo, button)

        # source.addTask("AliasObjectAlphaTo",
        #                Object=self.btn_close_photo, From=self.alpha_on, To=self.alpha_off, Time=self.hide_time)

        source.addDisable(self.btn_close_photo)

    def _onDeactivate(self):
        super(SurveyPhotoGallery, self)._onDeactivate()
        # print "SurveyPhotoGallery._onDeactivate"

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None