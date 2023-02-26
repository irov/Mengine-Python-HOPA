from Foundation.TaskManager import TaskManager

class HelpChain(object):
    # class - iterator switches bone board help objects

    def __init__(self, helpMovieChain, buttons, texts):
        self.chain = helpMovieChain
        self.buttons = buttons
        self.texts = texts
        self.currentState = -1
        self.complete = False

    def iterate(self):
        self.hide()
        self.currentState += 1
        help_lens = len(self.chain) - 1
        if self.currentState > help_lens or self.complete:
            return
        elif self.currentState == help_lens:
            self.complete = True
            pass
        CurrentMovie = self.chain[self.currentState]
        CurrentButton = self.buttons[self.currentState]
        CurrentText = self.texts[self.currentState]
        CurrentText.setEnable(True)
        CurrentButton.setEnable(True)
        CurrentButton.setInteractive(True)
        CurrentMovie.setEnable(True)
        CurrentMovie.setLoop(True)
        CurrentMovie.setPlay(True)
        pass

    def actionButton(self, buttonInstance):
        if buttonInstance in self.buttons:
            self.hide()
            pass
        pass

    def hide(self):
        [movie.setEnable(False) for movie in self.chain]
        [button.setEnable(False) for button in self.buttons]
        [text.setEnable(False) for text in self.texts]
        pass

    def turnOffHelp(self):
        self.complete = True
        pass

    def isCompletion(self):
        return self.complete
        pass

    def isSkipped(self):
        # worth it
        if self.currentState != -1:
            return True
            pass
        return False
        pass

class CasualHelper(object):
    TaskName = "BoneBoard_CasualHelp"
    Difficulties = [u"Casual"]

    def __init__(self, movie):
        self.movie = movie
        self.turnOff()
        pass

    def turnOff(self):
        self.movie.setEnable(False)
        pass

    def onShow(self):
        if Mengine.hasCurrentAccountSetting("Difficulty") is False:
            return
            pass

        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")

        if Difficulty not in CasualHelper.Difficulties:
            return
            pass

        if TaskManager.existTaskChain(CasualHelper.TaskName):
            return
            pass

        self.movie.setLoop(True)

        with TaskManager.createTaskChain(Name=CasualHelper.TaskName) as tc:
            tc.addTask("TaskEnable", Object=self.movie)
            tc.addTask("TaskMoviePlay", Movie=self.movie)
            pass
        pass

    def onHide(self):
        self.turnOff()
        pass

    def onDeactivate(self):
        if TaskManager.existTaskChain(CasualHelper.TaskName):
            TaskManager.cancelTaskChain(CasualHelper.TaskName)
            self.turnOff()
            pass
        pass