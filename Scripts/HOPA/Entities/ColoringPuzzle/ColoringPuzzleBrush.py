from Foundation.ArrowManager import ArrowManager

from HOPA.CursorManager import CursorManager

class ColoringPuzzleBrush(object):
    def __init__(self, movieObject):
        super(ColoringPuzzleBrush, self).__init__()
        self.movieObject = movieObject
        pass

    def __repr__(self):
        return " ColoringPuzzleBrush --- " + self.movieObject.getName()

    def show(self):
        self.movieObject.setEnable(True)
        movieEntity = self.movieObject.getEntity()
        movieEntityNode = self.movieObject.getEntityNode()
        animatable = movieEntity.getAnimatable()
        animatable.compile()

        slotOffset = movieEntity.getMovieSlot("offset")
        pos = slotOffset.getLocalPosition()
        self.movieObject.setOrigin(pos)

        arrow = Mengine.getArrow()
        itemNode = arrow.getCursorNode()
        # itemNode.removeAllChild()
        itemNode.addChild(movieEntityNode)

        cursorChildren = CursorManager.getCursorChildren()
        if len(cursorChildren) == 0:
            return

        currentCursor = cursorChildren[0]
        currentCursor.setEnable(False)

    def hide(self):
        movieEntity = self.movieObject.getEntity()
        movieEntity.removeFromParent()
        self.movieObject.setEnable(False)

        cursorChildren = CursorManager.getCursorChildren()
        if len(cursorChildren) == 0:
            return

        currentCursor = cursorChildren[0]
        currentCursor.setEnable(True)
