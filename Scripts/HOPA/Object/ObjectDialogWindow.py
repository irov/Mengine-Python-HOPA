from Foundation.Object.DemonObject import DemonObject


class ObjectDialogWindow(DemonObject):

    def run(self, content_style=None, text_ids=None, urls=None, text_args=None, icon_obj=None):
        if self.isActive():
            self.entity.run(content_style, text_ids, urls, text_args, icon_obj)

    def runPreset(self, preset_id, content_style=None, urls=None, text_args=None, icon_obj=None):
        if self.isActive():
            self.entity.runPreset(preset_id, content_style, urls, text_args, icon_obj)

    def setButtonBlock(self, state, movie_name):
        if self.isActive():
            self.entity.setButtonBlock(state, movie_name)

    @property
    def EVENT_WINDOW_APPEAR(self):
        if self.isActive():
            return self.entity.EVENT_WINDOW_APPEAR

    @property
    def EVENT_WINDOW_DISAPPEAR(self):
        if self.isActive():
            return self.entity.EVENT_WINDOW_DISAPPEAR
