from Foundation.Entity.BaseEntity import BaseEntity


class ZoomFrame(BaseEntity):
    def __init__(self):
        super(ZoomFrame, self).__init__()
        pass

    def _onActivate(self):
        super(ZoomFrame, self)._onActivate()
        #        print self.getScene()
        FrameGroup = self.object.getGroup()

        DemonObject = FrameGroup.getObject("Demon_ZoomFrame")
        DemonEntity = DemonObject.getEntity()
        DemonButton = FrameGroup.getObject("Demon_CloseZoom")
        DemonButtonEn = DemonButton.getEntity()
        origin = DemonEntity.getOrigin()
        DemonButtonEn.setOrigin(origin)

        pass

    def _onDeactivate(self):
        super(ZoomFrame, self)._onDeactivate()

    pass
