from Foundation.Entity.BaseEntity import BaseEntity

from Journal2Manager import Journal2Manager

class Journal2(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate("OpenPages")
        Type.addActionActivate("CurrentIndex", Update=Journal2.__updateIndex)
        Type.addAction("PageSize")
        pass

    def __init__(self):
        super(Journal2, self).__init__()
        self.Button_Left = None
        self.Button_Right = None
        self.onButtonClickObserver = None
        self.PosPolygon = None
        self.currentViewedPages = []
        pass

    def __updateIndex(self, value):
        self.loadPage(value)
        pass

    def loadPage(self, value):
        self.clearPreviousPage()
        i1 = value * self.PageSize
        i2 = value * self.PageSize + self.PageSize
        showPages = self.OpenPages[i1:i2]
        for index, pageID in enumerate(showPages):
            moviePos = self.PosPolygon[index]
            movie = Journal2Manager.getPage(pageID)
            movie.setPosition(moviePos)
            movie.setEnable(True)
            self.currentViewedPages.append(movie)
            pass
        pass

    def clearPreviousPage(self):
        for movie in self.currentViewedPages:
            movie.setEnable(False)
            pass
        self.currentViewedPages = []
        pass

    def disableAllPages(self):
        allPages = Journal2Manager.getAllPages()
        for movie in allPages.values():
            movie.setEnable(False)
            pass
        pass

    def _onPreparation(self):
        super(Journal2, self)._onPreparation()
        self.disableAllPages()

        self.Button_Left = self.object.getObject("Button_Left")
        self.Button_Left.setInteractive(True)
        self.Button_Left.setEnable(False)

        self.Button_Right = self.object.getObject("Button_Right")
        self.Button_Right.setInteractive(True)
        self.Button_Right.setEnable(False)

        Socket = self.object.getObject("Socket_PagePoint")
        self.PosPolygon = Socket.getPolygon()
        pass

    def _onActivate(self):
        super(Journal2, self)._onActivate()
        self.onButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        self.checkButtons()
        pass

    def checkButtons(self):
        if self.CurrentIndex == 0:
            self.Button_Left.setEnable(False)
            pass
        else:
            self.Button_Left.setEnable(True)
            pass

        if self.CurrentIndex < len(self.OpenPages) / self.PageSize:
            self.Button_Right.setEnable(True)
            pass
        else:
            self.Button_Right.setEnable(False)
            pass
        pass

    def __onButtonClick(self, button):
        if button is not self.Button_Left and button is not self.Button_Right:
            return False
            pass

        if button is self.Button_Left:
            newIndex = self.CurrentIndex - 1
            pass

        if button is self.Button_Right:
            newIndex = self.CurrentIndex + 1
            pass
        self.object.setCurrentIndex(newIndex)
        self.checkButtons()
        return False
        pass

    def _onDeactivate(self):
        super(Journal2, self)._onDeactivate()
        Notification.removeObserver(self.onButtonClickObserver)
        pass

    pass
