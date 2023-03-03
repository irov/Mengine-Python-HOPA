from Foundation.System import System


class SystemEditBox(System):
    s_active_edit_boxes = []

    def _onParams(self, params):
        super(SystemEditBox, self)._onParams(params)

    def _onRun(self):
        self.addObserver(Notificator.onEditboxSetActive, self.__changeActiveEditBoxes)
        return True

    def __changeActiveEditBoxes(self, name, state):
        if state is True:
            if name not in SystemEditBox.s_active_edit_boxes:
                SystemEditBox.s_active_edit_boxes.append(name)
        else:
            if name in SystemEditBox.s_active_edit_boxes:
                SystemEditBox.s_active_edit_boxes.remove(name)

        return False

    def _onStop(self):
        pass

    @staticmethod
    def hasActiveEditbox():
        if len(SystemEditBox.s_active_edit_boxes) != 0:
            return True
        return False
