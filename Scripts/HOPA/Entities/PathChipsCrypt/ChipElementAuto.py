from ChipElement import ChipElement
from Path import Path

class ChipElementAuto(ChipElement):
    def __init__(self):
        super(ChipElementAuto, self).__init__()
        self.hotspot = None
        self.offset = (0, 0)
        pass

    def _onMouseButtonEvent(self, context, event):
        if event.button != 0:
            return False
            pass

        if self.isBlock() is True:
            return False
            pass

        if event.isDown is False:
            return False
            pass

        if self.isCanMove() is False:
            return False
            pass

        if self.moveToDestination() is False:
            return False
            pass

        self.setBlock(True)
        self.endWalking()
        return False
        pass

    def _onEndMoviePlay(self):
        self.setBlock(False)
        self.view.setBlockHover(False)
        Notification.notify(Notificator.onPlaceChip, self)
        pass

    def moveToDestination(self):
        connections = Path.getActiveConnects(self.homeSlot)
        if len(connections) != 1:
            return False
            pass

        Connection = connections[0]
        moving = Connection[1]
        self.destinationSlot = Connection[0]
        self.setMoving(moving)
        self.moving.goTo(self.homeSlot)
        self.view.setBlockHover(True)

        Notification.notify(Notificator.onBeginMovingChip, self)
        self.moving.playTo(self.destinationSlot, self._onEndMoviePlay)
        pass

    pass
