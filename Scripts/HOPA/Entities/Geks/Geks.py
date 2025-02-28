from Foundation.TaskManager import TaskManager
from HOPA.GeksManager import GeksManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class Geks(Enigma):
    def __init__(self):
        super(Geks, self).__init__()
        self.buttons = []
        self.currentListButtons = []
        self.activeButton = None
        self.listAllButtons = []
        self.nextButton1 = None
        self.nextButton2 = None
        self.levelsCount = None
        pass

    def _stopEnigma(self):
        if self.nextButton2 is not None:
            self.nextButton2.setInteractive(False)
        if self.nextButton1 is not None:
            self.nextButton1.setInteractive(False)
            pass

        Notification.removeObserver(self.onButtonClickObserver)
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def _playEnigma(self):
        self.onButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self._onButtonClick)

        Geks = GeksManager.getGeks(self.EnigmaName)

        self.listsButtons = Geks.listButtons
        self.listAllButtons = Geks.listAllButtons
        self.levelsCount = len(self.listAllButtons)

        firstButton = self.listAllButtons[0][0]
        firstButton.setInteractive(True)

        pass

    def _updateButtonEnable(self):
        levelIndex = None
        for level in self.listAllButtons:
            if self.activeButton in level:
                levelIndex = self.listAllButtons.index(level)
                buttonIndex = level.index(self.activeButton)
                pass
            pass

        if self.nextButton1 == self.activeButton:
            self.nextButton2.setInteractive(False)
            pass
        elif self.nextButton2 == self.activeButton:
            self.nextButton1.setInteractive(False)
            pass

        self.nextButton1 = self.listAllButtons[levelIndex + 1][buttonIndex]
        self.nextButton1.setInteractive(True)
        self.nextButton2 = self.listAllButtons[levelIndex + 1][buttonIndex + 1]
        self.nextButton2.setInteractive(True)
        pass

    def _resetEnigma(self):
        self.currentListButtons = []
        for level in self.listAllButtons:
            for button in level:
                buttonEntity = button.getEntity()
                button.setBlockState(False)
                buttonEntity.setState("onUp")
                pass
            pass

        self.nextButton2.setInteractive(False)
        self.nextButton1.setInteractive(False)
        firstButton = self.listAllButtons[0][0]
        firstButton.setInteractive(True)
        return
        pass

    def _autoWin(self):
        index = Mengine.range_rand(0, len(self.listsButtons))
        list = self.listsButtons[index]
        for button in list:
            button.setBlockState(True)
            buttonEntity = button.getEntity()
            buttonEntity.setState("onDown")
            pass
        # for level in self.listAllButtons:
        #    for button in level:
        #       button.setInteractive(False)
        #      pass
        # pass

        with TaskManager.createTaskChain(Cb=self._complete) as tc:
            tc.addDelay(1.5 * 1000)  # speed fix
            pass
        pass

    def _onButtonClick(self, button):
        for buttons in self.listAllButtons:
            if button in buttons:
                self.activeButton = button
                button.setBlockState(True)
                buttonEntity = button.getEntity()
                buttonEntity.setState("onDown")

                self.currentListButtons.append(button)

                for list in self.listsButtons:
                    if list == self.currentListButtons:
                        with TaskManager.createTaskChain(Cb=self._complete) as tc:
                            tc.addDelay(1 * 1000)  # speed fix
                            pass
                        return False
                        pass
                    pass

                if len(self.currentListButtons) == self.levelsCount:
                    self.currentListButtons = []
                    for level in self.listAllButtons:
                        for button in level:
                            buttonEntity = button.getEntity()
                            button.setBlockState(False)
                            buttonEntity.setState("onUp")
                            pass
                        pass

                    self.nextButton2.setInteractive(False)
                    self.nextButton1.setInteractive(False)
                    firstButton = self.listAllButtons[0][0]
                    firstButton.setInteractive(True)
                    return False
                    pass

                button.setInteractive(False)
                self._updateButtonEnable()
                pass
            pass

        return False

    def _onDeactivate(self):
        super(Geks, self)._onDeactivate()

        self.buttons = []
        self.currentListButtons = []
        self.activeButton = None
        for buttons in self.listAllButtons:
            for button in buttons:
                button.setBlockState(False)
                buttonEntity = button.getEntity()
                buttonEntity.setState("onUp")
                pass
            pass
        self.listAllButtons = []
        self.nextButton1 = None
        self.nextButton2 = None
        self.levelsCount = None
        pass

    def _complete(self, isSkip):
        self.object.setParam("Play", False)
        self.enigmaComplete()
        pass

    pass
