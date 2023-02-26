from Foundation.Object.DemonObject import DemonObject

class ObjectCloseZoom(DemonObject):
    def _onParams(self, params):
        super(ObjectCloseZoom, self)._onParams(params)
        pass

    def getButtonClose(self):
        buttonClose = self.getObject("Button_CloseZoom")
        return buttonClose
        pass
    pass