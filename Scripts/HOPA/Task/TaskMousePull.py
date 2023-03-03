from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from Notification import Notification


class TaskMousePull(MixinObserver, Task):
    s_directions = ["Up", 'UpRight', 'Right', "DownRight", "Down", "DownLeft", "Left", "UpLeft"]
    s_angle = [i * 360 / len(s_directions) for i in range(len(s_directions))]

    def _onParams(self, params):
        super(TaskMousePull, self)._onParams(params)

        self.Direction = params.get("Direction")
        self.MinDistance = params.get("Distance")
        self.BlockDistance = 30

        self.baseDirection = map(self.rotateVector, TaskMousePull.s_angle)
        self.base = dict(zip(TaskMousePull.s_directions, self.baseDirection))
        self.sigma = 20 * 3.14 / 180
        pass

    def _onInitialize(self):
        super(TaskMousePull, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.Direction not in TaskMousePull.s_directions:
                self.initializeFailed("TaskMousePull invalid Direction %s" % (self.Direction,))
                pass
            pass
        pass

    def _onRun(self):
        arrow = Mengine.getArrow()
        self.startPoint = arrow.getLocalPosition()

        self.addObserver(Notificator.onMouseButtonEvent, self.__PullListener)

        return False
        pass

    def __PullListener(self, event):
        if event.isDown is True:
            return False
            pass
        arrow = Mengine.getArrow()
        endPoint = arrow.getLocalPosition()

        pullVector = (self.startPoint[0] - endPoint[0], self.startPoint[1] - endPoint[1])
        size_vect = pullVector[0] ** 2 + pullVector[1] ** 2

        if size_vect < self.MinDistance ** 2:
            Notification.notify(Notificator.onMousePull, self.Direction, False)  # min dist not accept
            return True
            pass

        base = self.base[self.Direction]
        self.validateDirection(base, pullVector)
        return True
        pass

    def validateDirection(self, baseDir, customDir):
        x, y = baseDir  # norm vector 1
        X, Y = customDir
        customNorma = ((X ** 2 + Y ** 2) ** 0.5)

        if customNorma < self.MinDistance:
            return False
            pass

        delta = Mengine.acosf((x * X + y * Y) / customNorma)
        if delta > self.sigma:
            return False
            pass

        Notification.notify(Notificator.onMousePull, self.Direction, True)
        return True
        pass

    def rotateVector(self, Angle):
        Angle = Angle * 3.14159 / 180  # from degree to radian
        baseX, baseY = 0, 1
        rotX = baseX * Mengine.cosf(Angle) - baseY * Mengine.sinf(Angle)
        rotY = baseX * Mengine.sinf(Angle) + baseY * Mengine.cosf(Angle)
        return rotX, rotY

