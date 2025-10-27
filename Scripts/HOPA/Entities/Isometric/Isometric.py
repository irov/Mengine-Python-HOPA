import math

from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.ObjectManager import ObjectManager


class Isometric(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction("Animations")
        pass

    def __init__(self):
        super(Isometric, self).__init__()

        self.animations = [None] * 8
        self.isometricAngle = 0.0
        self.isometricIndex = 0
        self.currentAnimation = None
        pass

    def _onInitialize(self, obj):
        super(Isometric, self)._onInitialize(obj)
        for index, resource in enumerate(self.Animations):
            animation = Mengine.createNode("Movie")
            animation.disable()
            resource.compile()
            animation.setResourceMovie(resource)
            animation.setLoop(True)

            self.addChild(animation)

            self.animations[index] = animation
            pass
        pass

    def _onFinalize(self):
        super(Isometric, self)._onFinalize()

        for animation in self.animations:
            Mengine.destroyNode(animation)
            pass

        self.animations = []
        pass

    def _onActivate(self):
        super(Isometric, self)._onActivate()

        self.currentAnimation = self.animations[self.isometricIndex]
        self.currentAnimation.enable()
        self.currentAnimation.play()
        pass

    def _onDeactivate(self):
        super(Isometric, self)._onDeactivate()

        self.currentAnimation.disable()
        pass

    def setIsometricAngle(self, angle):
        self.isometricAngle = angle
        rad = math.radians(angle)

        v = Mengine.vec2f(Mengine.cosf(rad), -Mengine.sinf(rad))
        new_isometricIndex = Mengine.rotateToTrimetric(v, (2, 1), (2, -1))

        self.__setCurrentAnm(new_isometricIndex)
        pass

    def __setCurrentAnm(self, index):
        if index is self.isometricIndex:
            return
            pass

        if self.currentAnimation is not None:
            self.currentAnimation.disable()
            pass

        self.isometricIndex = index
        self.currentAnimation = self.animations[self.isometricIndex]
        self.currentAnimation.enable()
        self.currentAnimation.play()
        pass

    def getCurrentAnmMovieObj(self):
        ResourceMovie = self.Animations[self.isometricIndex]
        Movie = ObjectManager.createObjectUnique("Movie", "Mov_%s" % (ResourceMovie), None, ResourceMovie=ResourceMovie)

        return Movie
        pass

    pass
