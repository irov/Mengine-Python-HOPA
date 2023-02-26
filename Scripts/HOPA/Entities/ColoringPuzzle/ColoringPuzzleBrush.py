from Foundation.ArrowManager import ArrowManager

class ColoringPuzzleBrush(object):
    def __init__(self, movieObject):
        super(ColoringPuzzleBrush, self).__init__()
        self.movieObject = movieObject
        pass

    def __repr__(self):
        return " ColoringPuzzleBrush --- " + self.movieObject.getName()
        pass

    def show(self):
        self.movieObject.setEnable(True)
        movieEntity = self.movieObject.getEntity()
        movieEntityNode = self.movieObject.getEntityNode()
        animatable = movieEntity.getAnimatable()
        animatable.compile()

        slotOffset = movieEntity.getMovieSlot("offset")
        pos = slotOffset.getLocalPosition()
        self.movieObject.setOrigin(pos)

        arrow = ArrowManager.getArrow()
        itemNode = arrow.getCursorNode()
        # itemNode.removeAllChild()
        itemNode.addChild(movieEntityNode)

        currentCursor = ArrowManager.getCursorChildren()
        if currentCursor is None:
            return
            pass

        currentCursor.setEnable(False)
        pass

    def hide(self):
        movieEntity = self.movieObject.getEntity()
        movieEntity.removeFromParent()
        self.movieObject.setEnable(False)

        currentCursor = ArrowManager.getCursorChildren()
        if currentCursor is None:
            return
            pass

        currentCursor.setEnable(True)
        pass