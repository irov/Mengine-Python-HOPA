from Foundation.Entity.BaseEntity import BaseEntity


class MenuGreeting(BaseEntity):
    def __init__(self):
        super(MenuGreeting, self).__init__()
        self.attachText = False
        pass

    def _onActivate(self):
        self.updateText()
        pass

    def _onDeactivate(self):
        self.movesBackText()
        pass

    def updateText(self):
        AccountName = Mengine.getCurrentAccountName()
        Default = Mengine.getCurrentAccountSettingBool("Default")
        if AccountName == "" or AccountName is None or Default is True:
            text = self.object.getObject("Text_Greeting")
            text.setEnable(False)

            return False
            pass
        else:
            text = self.object.getObject("Text_Greeting")
            text.setEnable(True)
            pass

        Name = Mengine.getAccountSetting(AccountName, "Name")

        text = self.object.getObject("Text_Greeting")

        textEn = text.getEntity()

        textField = textEn.getTextField()
        textField.setTextId("ID_MenuGreeting")
        textField.setTextFormatArgs(Name)

        self.object.setEnable(True)

        if self.object.hasObject("Movie_Greeting") is True:
            movieGreeting = self.object.getObject("Movie_Greeting")
            movieEn = movieGreeting.getEntity()

            textEn.removeFromParent()

            slotNode = movieEn.getMovieSlot("Greeting")
            slotNode.addChild(textEn)

            text.setPosition((0, 0, 0))
            self.attachText = True
            pass
        pass

    def movesBackText(self):
        if self.attachText is True:
            text = self.object.getObject("Text_Greeting")
            textEn = text.getEntity()
            textEn.removeFromParent()
