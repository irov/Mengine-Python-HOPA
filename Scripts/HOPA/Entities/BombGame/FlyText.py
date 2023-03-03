Enigma = Mengine.importEntity("Enigma")


class FlyText(object):
    def __init__(self, Game, StartPos, Text):
        self.Game = Game
        self.StartPos = StartPos
        self.CurrentPos = StartPos
        self.Text = Text

        self.Time = 1000
        self.Move_On = (0, -60.0)
        self.Move_On_Tic = (self.Move_On[0] / self.Time, self.Move_On[1] / self.Time)

        self.StartFlyTime = Mengine.getTimeMs()
        self.EndFlyTime = self.StartFlyTime + self.Time
        pass

    def Fly(self):
        time = Mengine.getTimeMs()
        if (time >= self.EndFlyTime):
            return True
            pass
        dif = time - self.StartFlyTime

        x = dif * self.Move_On_Tic[0] + self.StartPos[0]
        y = dif * self.Move_On_Tic[1] + self.StartPos[1]

        color = (1, 1, 1, 1.0 - 0.8 * dif / self.Time)
        self.Text.setLocalColor(color)

        self.CurrentPos = (x, y)
        self.Text.setLocalPosition(self.CurrentPos)
        return False
