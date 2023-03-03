from Foundation.TaskManager import TaskManager
from Functor import Functor
from Notification import Notification

from Field import Field
from MagneticLabyrinthManager import MagneticLabyrinthManager


Enigma = Mengine.importEntity("Enigma")


class MagneticLabyrinth(Enigma):
    TaskName = "MagneticLabyrinth_Move"

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        pass

    def __init__(self):
        super(MagneticLabyrinth, self).__init__()
        self.Field = None
        self.Ball = None
        self.MovieFall = None
        self.buttonsMap = {}
        pass

    def _stopEnigma(self):
        self.Field = None
        self.buttonsMap = {}
        self.Ball.setEnable(False)
        self.Ball = None
        self.object.removeObject("Movie_Main")
        Notification.removeObserver(self.ButtonHandler)
        if TaskManager.existTaskChain(MagneticLabyrinth.TaskName):
            TaskManager.cancelTaskChain(MagneticLabyrinth.TaskName)
            pass
        pass

    def _skipEnigma(self):
        self.autowin()
        pass

    def _playEnigma(self):
        self.ButtonHandler = Notification.addObserver(Notificator.onButtonClick, self.on_button_cb)
        self.restore()
        pass

    def restore(self):
        data = MagneticLabyrinthManager.getGameData(self.EnigmaName)
        self.speed = data.getSpeed()
        SocketBoundary = self.object.getObject("Socket_Border")
        Button_Down = self.object.getObject("Button_Down")
        Button_Up = self.object.getObject("Button_Up")
        Button_Left = self.object.getObject("Button_Left")
        Button_Right = self.object.getObject("Button_Right")
        self.buttonsMap = {Button_Right: 1, Button_Down: 2, Button_Left: 3, Button_Up: 4}
        [button.setInteractive(True) for button in self.buttonsMap.keys()]
        BoundaryPolygon = SocketBoundary.getParam("Polygon")
        self.Field = Field(BoundaryPolygon, data)
        self.Field.setEscaping()
        self.Field.initFieldCursor()
        cord2ds = self.Field.getFieldCursor()
        self.Ball = self.object.generateObject("Movie_Main", "Movie_Ball")
        self.Ball.setPosition(cord2ds)
        self.Ball.setLoop(True)
        self.MovieFall = self.object.getObject("Movie_Fall")
        self.MovieFall.setEnable(False)  # self.boundaries()

    def boundaries(self):
        # for only tests
        cordsBound = self.Field.getInternBoundaries()
        for i, cord in enumerate(cordsBound):
            ball = self.object.generateObject("Movie_%d" % (i,), "Movie_Ball")
            ball.setPosition(cord)
            ball.setPlay(True)
            pass
        pass

    def on_button_cb(self, button):
        if button in self.buttonsMap:
            if TaskManager.existTaskChain(MagneticLabyrinth.TaskName):
                return False
                pass
            direction = self.buttonsMap[button]
            self.Field.defineMove(direction)
            track = self.Field.track

            time = track / 5.0 * 1000  # speed fix
            new_position = self.Field.getFieldCursor()
            BallEn = self.Ball.getEntity()
            escapedBool = self.Field.isEscaped()
            fallDown = self.Field.isFallDown()
            with TaskManager.createTaskChain(Name=MagneticLabyrinth.TaskName,
                                             Cb=Functor(self._complete, escapedBool)) as tc:
                tc.addTask("TaskMoviePlay", Movie=self.Ball, Wait=False)
                tc.addTask("TaskNodeMoveTo", Node=BallEn, Time=time, To=new_position, Speed=self.speed)
                tc.addTask("TaskFunction", Fn=self.Ball.setPosition, Args=(new_position,))
                tc.addTask("TaskFunction", Fn=self.Ball.setPlay, Args=(False,))
                if fallDown is True:
                    tc.addTask("TaskEnable", Object=self.Ball, Value=False)
                    tc.addTask("TaskEnable", Object=self.MovieFall)
                    tc.addTask("TaskMoviePlay", Movie=self.MovieFall)
                    tc.addTask("TaskEnable", Object=self.MovieFall, Value=False)
                    tc.addTask("TaskFunction", Fn=self.returnBall)
                    tc.addTask("TaskEnable", Object=self.Ball)
                pass
            pass
        return False
        pass

    def returnBall(self):
        start_position = self.Field.returnToStart()
        if start_position is not None:
            self.Ball.setPosition(start_position)
            pass
        pass

    def _resetEnigma(self):
        self.returnBall()
        pass

    def _complete(self, isSkip, escaped):
        if escaped is False:
            return
            pass
        self.autowin()
        pass

    def autowin(self):
        self.Ball.setEnable(False)
        self.object.setParam("Play", False)
        self.enigmaComplete()
        pass
