from Foundation.TaskManager import TaskManager
from Notification import Notification

from BallStack import BallStack
from ChasingSystem import ChasingSystem


class Gun(object):

    def __init__(self, guns_movies, ball_movies, socketObj, generic, pattern):
        self.guns = guns_movies
        self.socket = socketObj
        self.block_observe = True
        self.NotDisableGuns = []
        self.faster = 4
        self.balls = ball_movies
        self.generic = generic
        self.after_init()
        self.pattern = pattern
        self.position_object = []
        self.generic_count = 0
        self.ball_limit = 4
        self.head_shoots = 0
        self.gun_with_slot = None
        self.tasks_pool = []
        self.ball_bucket = []
        pass

    def after_init(self):
        self.sectors = len(self.guns)
        for gun in self.guns:
            gun.setEnable(False)
            gun.setSpeedFactor(self.faster)

        for ball in self.balls:
            ball.setSpeedFactor(self.faster)

        first_gun = len(self.guns) // 2
        init_gun = self.guns[first_gun]
        init_gun.setEnable(True)
        self.nowGun = first_gun
        #        self.trowStack(init_gun)
        self.TargetEnter = Notification.addObserver(Notificator.onSocketMouseEnter, self.onMouseEnter)
        # self.TargetMove = Notification.addObserver(Notificator.onMouseMove, self.onMouseMove)
        self.TargetMove = Mengine.addMouseMoveHandler(self.onMouseMove)

        # self.TargetMove2 = Notification.addObserver(Notificator.onMouseButtonEvent, self.onMouseMove)

        self.TargetLeave = Notification.addObserver(Notificator.onSocketMouseLeave, self.onMouseLeave)
        self.TargetClick = Notification.addObserver(Notificator.onSocketClick, self.onTargetClick)
        pass

    def setLimit(self, limitInt):
        self.ball_limit = limitInt
        pass

    def setupGeometry(self, gun_back_point, attitude_point, wind_size):
        self.gun_back_point = gun_back_point
        self.attitude_point = attitude_point
        self.wind_size = wind_size
        pass

    def destroy(self):  # clean up notification
        self.removeStack()
        Notification.removeObserver(self.TargetEnter)
        # Notification.removeObserver(self.TargetMove)
        Notification.removeObserver(self.TargetLeave)
        Notification.removeObserver(self.TargetClick)
        [TaskManager.cancelTaskChain(taskName) for taskName in self.tasks_pool if TaskManager.existTaskChain(taskName)]
        for ball in self.ball_bucket:
            ball.removeFromParent()
            #            ballEn  = self.generic.getObject(ball).getEntity()
            #            DemonEn = self.generic.getEntity()
            #            DemonEn.addChild(ballEn)
            pass
        pass

    def onMouseEnter(self, socket):
        if socket == self.socket:
            self.block_observe = True
            pass
        return False

    def onMouseMove(self, event):
        if self.block_observe:
            self.__onMouseMove()
        pass

    def onMouseLeave(self, socket):
        if socket == self.socket:
            self.block_observe = False
            pass
        return False
        pass

    def __onMouseMove(self):
        arrow_node = Mengine.getArrowNode()
        point = arrow_node.getLocalPosition()
        numGun = self.getGunMovieFromPos(point)
        if numGun != self.nowGun:
            self.nowGun = numGun
            self.removeStack()  # clean slot
            for i, movie_gun in enumerate(self.guns):
                if i == numGun:
                    movie_gun.setEnable(True)
                    self.trowStack(movie_gun)
                else:
                    movie_gun.setEnable(False)
                pass
            pass
        pass

    def onTargetClick(self, socket):
        if socket == self.socket:
            self.makeShot()
        return False

    def is_head_shot(self, pos):
        if ChasingSystem.current is None:
            return False

        target_pos = ChasingSystem.current.getCurrentPosition()
        if target_pos is None:  # if already hit
            return False

        hit_positions = self.getHitPositions()
        for i, position in enumerate(hit_positions):
            if abs(target_pos - position) < 50:
                self.head_shoots += 1
                Notification.notify(Notificator.onChased, ChasingSystem.current)
                if len(self.position_object) > i:
                    del self.position_object[i]  # already hit
                return True
            else:
                return False

    def getGunMovieFromPos(self, point):  # OMG
        # refactoring
        """
         x3 = x1+(x2-x1)(y3-y1)/(y2-y1)
        """
        size = self.wind_size[0]
        x2, y2 = point.x, point.y  # named tuple
        y3 = self.attitude_point[1]
        x1, y1 = self.gun_back_point
        diffX2X1 = x2 - x1
        diffY3Y1 = y3 - y1
        diffY2Y1 = y2 - y1
        if diffX2X1 == 0:
            X = x1
        elif diffY2Y1 == 0:
            return self.nowGun
        else:
            X = x1 + diffX2X1 * diffY3Y1 / diffY2Y1
        #        X = point[0]
        if X < 0 or X > size:
            return self.nowGun
        current_gun = int((self.sectors * X) / size)
        return current_gun
        pass

    def getDuration(self):
        ball_movie = self.balls[self.nowGun]
        duration = ball_movie.getDuration() / self.faster
        return duration
        pass

    def makeShot(self):
        if self.ball_limit == 0:
            Notification.notify(Notificator.onEnigmaReset)
            return
        else:
            self.ball_limit -= 1
            pass

        movie = self.balls[self.nowGun]

        if movie.getParam("Play") is True:
            return

        movie.setPosition((0, 0))
        mov_entity = movie.getEntity()
        ballNode = mov_entity.getMovieSlot("ball")
        BallName = "BallShooting%d" % (self.generic_count)
        temp_ball = self.generic.generateObject(BallName, self.pattern[(3 - self.ball_limit) % len(self.pattern)])

        temp_ball.setEnable(True)
        temp_ball.setPosition((0, 0))

        movie.setEnable(True)
        self.generic_count += 1
        temp_entity = temp_ball.getEntity()
        ballNode.addChild(temp_entity)

        self.ball_bucket.append(temp_ball)

        positionNode = mov_entity.getMovieSlot("position")
        self.position_object.append(positionNode)

        hasEvent = mov_entity.hasMovieEvent("onCross")
        if hasEvent is True:  # test
            mov_entity.setMovieEvent("onCross", self.is_head_shot)
            pass
        TaskName = "ShootingGun%d" % (len(self.tasks_pool) + 1,)
        self.tasks_pool.append(TaskName)
        with TaskManager.createTaskChain(Name=TaskName) as tc_fly:
            tc_fly.addFunction(BallStack.turn_state)
            tc_fly.addTask("TaskMoviePlay", Movie=movie, LastFrame=False)
            tc_fly.addFunction(mov_entity.setTiming, 1)
            tc_fly.addFunction(mov_entity.setFirstFrame)
            tc_fly.addFunction(temp_entity.removeFromParent)
            tc_fly.addFunction(self.removePositionInstance, positionNode)
            if hasEvent is True:
                tc_fly.addFunction(mov_entity.setMovieEvent, "onCross", None)
                pass
            tc_fly.addDisable(temp_ball,)
        pass

    def removePositionInstance(self, positionNode):
        if positionNode in self.position_object:
            self.position_object.remove(positionNode)
            pass
        pass

    def getHitPositions(self):
        positions = [vec3.getWorldPosition()[0] for vec3 in self.position_object]
        return positions

    def trowStack(self, movie):
        StackEntity = BallStack.get()
        movie_en = movie.getEntity()

        stackNode = movie_en.getMovieSlot("stack")
        stackNode.addChild(StackEntity)
        self.gun_with_slot = stackNode
        pass

    def removeStack(self):
        StackEntity = BallStack.get()
        if self.gun_with_slot:
            if (StackEntity):
                StackEntity.removeFromParent()

            # print (dir(self.gun_with_slot))
            # self.gun_with_slot.removeChild(StackEntity)
            pass
        pass
