from Foundation.Entity.BaseEntity import BaseEntity


class Chip(BaseEntity):
    def __init__(self):
        super(Chip, self).__init__()
        pass

    def _onActivate(self):
        self.button = None
        self.buttonObject = None
        self.buttonObject = self.object.getObject("Button_Chip")
        self.button = self.buttonObject.getEntity()
        sprites = self.button.getSprites()
        for sprite in sprites:
            sprite.setLocalPosition((0, 0))
            pass

        imageSize = self.getSize()
        polygon = []
        polygon.append((0.0, 0.0))
        polygon.append((imageSize.x, 0.0))
        polygon.append((imageSize.x, imageSize.y))
        polygon.append((0.0, imageSize.y))
        self.buttonObject.setPolygon(polygon)
        pass

    def init(self):
        self.buttonObject.setInteractive(True)
        pass

    def _onButtonMouseEnter(self, button):
        return True
        pass

    def getSize(self):
        image = self.button.getSprite()
        size = image.getSurfaceSize()
        return size
        pass

    def blockHover(self, value):
        if value is True:
            self.buttonObject.setParam("BlockState", True)
            pass
        else:
            self.buttonObject.setParam("BlockState", False)
            self.button.setState("onUp")
            pass
        pass

    def getHotSpot(self):
        hotSpot = self.button.getHotSpot()
        return hotSpot
        pass

    def _onInitialize(self, obj):
        super(Chip, self)._onInitialize(obj)
        pass

    def _onFinalize(self):
        super(Chip, self)._onFinalize()
        pass
