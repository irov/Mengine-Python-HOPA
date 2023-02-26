import Foundation.Utils as Utils
from HOPA.TrafficJamManager import TrafficJamManager
from Notification import Notification

class TrafficJamElement(object):
    def __init__(self, trafficjam, sprite, hotspot, element):
        self.trafficjam = trafficjam
        self.sprite = sprite
        self.hotspot = hotspot
        self.element = element

        self.x = None
        self.y = None

        self.x_clip_left = None
        self.x_clip_right = None

        self.y_clip_top = None
        self.y_clip_bottom = None

        self.offset = None
        pass

    def clearPole(self, value):
        pos = self.sprite.getLocalPosition()
        rpos = self.trafficjam.getPoleCell(pos.x, pos.y)

        if self.element.horizontal is True:
            lx = int(rpos[0] + 0.1)
            rx = int(rpos[0] + 0.9) + self.element.size
            for i in xrange(lx, rx):
                self.trafficjam.setPole(i, self.y, value)
                pass
        else:
            ty = int(rpos[1] + 0.1)
            by = int(rpos[1] + 0.9) + self.element.size

            for i in xrange(ty, by):
                self.trafficjam.setPole(self.x, i, value)
                pass
            pass
        pass

    def setPosition(self, x, y):
        self.x = x
        self.y = y
        pass

    def reset(self):
        self.sprite.resetTransformation()
        pos_x = self.trafficjam.CellPosition[0] + self.element.pos[0] * self.trafficjam.CellSize[0]
        pos_y = self.trafficjam.CellPosition[1] + self.element.pos[1] * self.trafficjam.CellSize[1]

        self.sprite.setLocalPosition((pos_x, pos_y))

        self.setPosition(self.element.pos[0], self.element.pos[1])
        self.clearPole(0)

        x, y = self.element.pos
        if self.element.horizontal is True:
            for pos in range(self.element.size):
                self.trafficjam.setPole(x + pos, y, 1)
                pass
            pass
        else:
            for pos in range(self.element.size):
                self.trafficjam.setPole(x, y + pos, 1)
                pass
            pass
        pass

    def onActivate(self):
        self.hotspot.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent)
        self.hotspot.setEventListener(onGlobalHandleMouseMove=self._onGlobalMouseMove, onGlobalHandleMouseButtonEvent=self._onGlobalMouseButtonEvent)

        self.hotspot.enable()

        self.sprite.addChild(self.hotspot)

        self.reset()
        pass

    def onDeactivate(self):
        if self.hotspot is not None:
            Mengine.destroyNode(self.hotspot)
            self.hotspot = None
            pass

        self.trafficjam = None
        self.sprite = None
        self.element = None
        pass

    def _onMouseButtonEvent(self, touchId, x, y, button, isDown, isPressed):
        if button != 0:
            return False

        if isDown is True:
            Notification.notify(Notificator.onTrafficJamClick, self.trafficjam)
            self.hotspot.enableGlobalMouseEvent(True)

            sliderPos = self.sprite.getLocalPosition()

            arrow = Mengine.getArrow()
            arrowPos = arrow.getWorldPosition()

            self.offset = (arrowPos.x - sliderPos.x, arrowPos.y - sliderPos.y)

            self.clearPole(0)

            if self.element.horizontal is True:
                self.x_clip_left = 0
                for i in range(0, self.x + 1):
                    if self.trafficjam.getPole(self.x - i, self.y) == 0:
                        self.x_clip_left = self.x - i
                    else:
                        break
                        pass
                    pass

                self.x_clip_right = self.x
                clip_right_size = self.trafficjam.PoleSize[0] - (self.x + self.element.size - 1)

                for i in range(1, clip_right_size + 1):
                    new_x = self.x + (self.element.size - 1) + i
                    if new_x == self.trafficjam.PoleSize[0]:
                        break

                    if self.trafficjam.getPole(new_x, self.y) == 0:
                        self.x_clip_right = new_x - (self.element.size - 1)
                    else:
                        break
                        pass
                    pass
            else:
                self.y_clip_top = 0
                for i in range(0, self.y + 1):
                    if self.trafficjam.getPole(self.x, self.y - i) == 0:
                        self.y_clip_top = self.y - i
                    else:
                        break
                        pass
                    pass

                self.y_clip_bottom = self.y
                clip_right_size = self.trafficjam.PoleSize[1] - (self.y + self.element.size - 1)

                for i in range(1, clip_right_size + 1):
                    new_y = self.y + (self.element.size - 1) + i
                    if new_y == self.trafficjam.PoleSize[1]:
                        break

                    if self.trafficjam.getPole(self.x, new_y) == 0:
                        self.y_clip_bottom = new_y - (self.element.size - 1)
                    else:
                        break
                        pass
                    pass
                pass

            pass

        return True
        pass

    def _onGlobalMouseMove(self, touchId, x, y, dx, dy):
        arrow = Mengine.getArrow()
        arrowPos = arrow.getWorldPosition()

        newPos = (arrowPos.x - self.offset[0], arrowPos.y - self.offset[1])

        x = self.x
        y = self.y

        if self.element.horizontal is True:
            v0 = self.trafficjam.CellPosition[0] + self.x_clip_left * self.trafficjam.CellSize[0]
            v1 = self.trafficjam.CellPosition[0] + self.x_clip_right * self.trafficjam.CellSize[0]

            newPos2 = Mengine.projectionPointToLine(newPos, (v0, 0.0), (v1, 0.0))

            x = (newPos2.x - self.trafficjam.CellPosition[0]) / self.trafficjam.CellSize[0]

            if x > self.x_clip_right:
                x = self.x_clip_right
            elif x < self.x_clip_left:
                x = self.x_clip_left
                pass
        else:
            v0 = self.trafficjam.CellPosition[1] + self.y_clip_top * self.trafficjam.CellSize[1]
            v1 = self.trafficjam.CellPosition[1] + self.y_clip_bottom * self.trafficjam.CellSize[1]

            newPos2 = Mengine.projectionPointToLine(newPos, (0.0, v0), (0.0, v1))

            y = (newPos2.y - self.trafficjam.CellPosition[1]) / self.trafficjam.CellSize[1]

            if y > self.y_clip_bottom:
                y = self.y_clip_bottom
            elif y < self.y_clip_top:
                y = self.y_clip_top
                pass
            pass

        sprite_x = self.trafficjam.CellPosition[0] + x * self.trafficjam.CellSize[0]
        sprite_y = self.trafficjam.CellPosition[1] + y * self.trafficjam.CellSize[1]

        self.sprite.setLocalPosition((sprite_x, sprite_y))

        new_x = int(x + 0.1)
        new_y = int(y + 0.1)

        self.setPosition(new_x, new_y)

        return
        pass

    def _onGlobalMouseButtonEvent(self, touchId, button, isDown):
        if button != 0:
            return False
            pass

        if isDown is False:
            self.clearPole(1)
            self.hotspot.enableGlobalMouseEvent(False)
            pass

        if self.element.main == 1:
            self.trafficjam.testWin(self.x, self.y)
            pass

        return
        pass
    pass

Enigma = Mengine.importEntity("Enigma")

class TrafficJam(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)

        Type.addAction(Type, "PoleSize")
        Type.addAction(Type, "CellWrap")
        Type.addAction(Type, "CellPosition")
        Type.addAction(Type, "Goal")
        pass

    def __init__(self):
        super(TrafficJam, self).__init__()

        self.elements = []
        self.pole = []
        pass

    def _playEnigma(self):
        TrafficJamDesc = TrafficJamManager.getTrafficJam(self.EnigmaName)

        self.CellSize = (self.CellWrap[1][0] - self.CellWrap[0][0], self.CellWrap[1][1] - self.CellWrap[0][1])
        self.pole = [0] * (self.PoleSize[0] * self.PoleSize[1])
        elements = TrafficJamDesc.elements

        for element in elements:
            Sprite_Element = self.object.getObject(element.sprite)

            Sprite_ElementEntity = Sprite_Element.getEntity()
            sprite = Sprite_ElementEntity.getSprite()

            hotspot = Utils.createBBSpriteHotspot("Sprite_Element", sprite)

            tj_element = TrafficJamElement(self, Sprite_ElementEntity, hotspot, element)

            self.elements.append(tj_element)

            tj_element.onActivate()
            pass
        pass

    def _resetEnigma(self):
        self.CellSize = (self.CellWrap[1][0] - self.CellWrap[0][0], self.CellWrap[1][1] - self.CellWrap[0][1])
        self.pole = [0] * (self.PoleSize[0] * self.PoleSize[1])
        for element in self.elements:
            element.reset()
            pass
        pass

    def _skipEnigma(self):
        self._onWinEnigma()
        return False
        pass

    def _onActivate(self):
        super(TrafficJam, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(TrafficJam, self)._onDeactivate()

        for element in self.elements:
            element.onDeactivate()
            pass

        self.elements = []
        pass

    def _skipEnigma(self):
        self._onWinEnigma()
        pass

    def _onWinEnigma(self):
        self.enigmaComplete()
        pass

    def setPole(self, x, y, value):
        index = x + y * int(self.PoleSize[0])
        self.pole[index] = value
        pass

    def getPole(self, x, y):
        index = x + y * int(self.PoleSize[0])
        value = self.pole[index]
        return value
        pass

    def getPoleCell(self, x, y):
        rx = (x - self.CellPosition[0]) / self.CellSize[0]
        ry = (y - self.CellPosition[1]) / self.CellSize[1]

        return (rx, ry)
        pass

    def testWin(self, x, y):
        if self.Goal[0] == x and self.Goal[1] == y:
            self._onWinEnigma()
            pass
        pass
    pass