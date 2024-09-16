from Foundation.TaskManager import TaskManager
from Notification import Notification


class ZumaTurret(object):
    FreeLength = 1000
    ShootSpeed = 500 * 0.001  # speed fix
    ViewPoint = (515, 345)
    BlockShoot = 0

    def __init__(self, Group, gunObj):
        self.Shoot = Notification.addObserver(Notificator.onMouseButtonEvent, self.__MakeShoot)
        self.group = Group
        self.Shoots = 0
        self.shootPattern = ["Sprite_Red", "Sprite_Blue", "Sprite_Yellow"]
        self.watcher = ZumaWatcher(gunObj)
        pass

    def __MakeShoot(self, event):
        if event.isDown is True:
            return False

        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        arrowPosition = arrow_node.getLocalPosition()

        #        arrowPosition= (arrowPosition[0],arrowPosition[1]-20)
        def findSolution(v2, v3):
            norma = ((v3[0] - v2[0]) ** 2 + (v3[1] - v2[1]) ** 2) ** 0.5
            xvector = v3[0] - v2[0]
            yvector = v3[1] - v2[1]

            x = ZumaTurret.FreeLength * xvector / norma
            y = ZumaTurret.FreeLength * yvector / norma
            point = (ZumaTurret.ViewPoint[0] + x, ZumaTurret.ViewPoint[1] + y)
            time = ZumaTurret.FreeLength / ZumaTurret.ShootSpeed
            return point, time

        def unblock(isSkip):
            self.Shoot = Notification.addObserver(Notificator.onMouseButtonEvent, self.__MakeShoot)

        pointTo, timeTo = findSolution(ZumaTurret.ViewPoint, arrowPosition)
        with TaskManager.createTaskChain() as tc:
            tc.addTask("AliasObjectMoveTo", Object=self.__generateShoot(), To=pointTo, Time=timeTo)
            tc.addTask("TaskDelay", Time=ZumaTurret.BlockShoot)
        unblock(True)
        return True
        pass

    @staticmethod
    def setCentreAtach(Obj):
        Ent = Obj.getEntity()
        Image = Ent.getSprite()
        origin = Image.getLocalImageCenter()
        #        print Obj.getPosition()
        position = Obj.getPosition()
        Obj.setOrigin(origin)
        newpos = (position[0] + origin[0], position[1] + origin[1])
        Obj.setPosition(newpos)

    def __generateShoot(self):
        color = self.shootPattern[self.Shoots % 3]
        Ball = self.group.generateObject("Shoot_Zuma_%d" % (self.Shoots,), color)
        self.Shoots += 1
        BallEn = Ball.getEntity()
        Image = BallEn.getSprite()
        origin = Image.getLocalImageCenter()

        Ball.setOrigin(origin)
        #        ZumaTurret.setCentreAtach(Ball)
        return Ball
        pass

    def stopTurel(self):
        Notification.removeObserver(self.Shoot)
        pass

    pass


class ZumaWatcher(object):

    def __init__(self, GunObject=None):
        self.Rotate = Notification.addObserver(Notificator.onMouseMove, self.__MakeRotate)
        self.GunObject = GunObject
        self.phaza = 1.15
        self.__preparation()
        pass

    def __preparation(self):
        ZumaTurret.setCentreAtach(self.GunObject)

    #        self.GunObject.setRotate(-1)

    def __MakeRotate(self, *args):
        arrow = Mengine.getArrow()
        arrow_node = arrow.getNode()
        arrowPosition = arrow_node.getLocalPosition()
        #        basePosition = (0,0)
        basePosition = self.GunObject.getPosition()
        dy = arrowPosition[1] - basePosition[1]
        dx = arrowPosition[0] - basePosition[0]  # or 0.0001 # in be for divide by zero
        #        Angle = Mengine.atanf(dy/dx)
        #        print Angle*180/3.141817
        dr = (dx, dy)
        Angle = Mengine.signed_angle(dr)
        #        print Angle*180/3.141817, Angle
        self.GunObject.setRotate(self.phaza - Angle)
        return False
        pass

    pass
