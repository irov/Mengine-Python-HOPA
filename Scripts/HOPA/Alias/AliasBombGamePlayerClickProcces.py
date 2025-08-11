from Foundation.Task.TaskAlias import TaskAlias

class AliasBombGamePlayerClickProcces(TaskAlias):
    def __init__(self):
        super(AliasBombGamePlayerClickProcces, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasBombGamePlayerClickProcces, self)._onParams(params)
        self.BombGame = params.get("BombGame")
        self.ClickPos = None
        self.ClickCell = None
        self.Bomb = [0]
        self.Dir = [0]
        self.Movie = [None]
        self.MoviePre = [None]
        pass

    def _onInitialize(self):
        super(AliasBombGamePlayerClickProcces, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        self.ClickCell = self.BombGame.Click
        self.ClickPos = self.BombGame.ClickMouse

        slot = self.BombGame.getSlot(self.ClickCell)
        Item = slot.Item
        itemType = Item.getItemType()

        if (itemType == 1 or itemType == 3):
            if (Item.Inivese is False):
                self.__PlaySimpleBomb(source, slot)
            pass
        elif (itemType == 2):
            if (Item.Inivese is False):
                self.__PlayMoveBomb(source, slot)
            pass
        elif (itemType >= 100):
            self.__PickItem(source, slot)
            pass

        pass

    def __PlaySimpleBomb(self, source, slot):
        self.Bomb[0] = self.BombGame.createBombClick(self.ClickCell)
        bomb = self.Bomb[0]
        bomb.PreExploud()
        mov = bomb.getPreExploudMovie()
        self.MoviePre[0] = [(mov, True)]

        def exp():
            bomb.Exploud()
            bomb.getMovie(self.Movie)
            pass

        def expEnd():
            bomb.ExploudEnd()
            pass

        source.addTask("AliasMultyplMovePlay", Movies=self.MoviePre)
        source.addFunction(exp)
        source.addTask("AliasMultyplMovePlay", Movies=self.Movie)
        source.addFunction(expEnd)
        pass

    def __PlayMoveBomb(self, source, slot):
        self.Bomb[0] = self.BombGame.createBombMove(self.ClickCell)

        def __SetMoveDir():
            currentMousePos = Mengine.getCursorPosition()
            res = self.Bomb[0].SetMoveDir(self.ClickPos, currentMousePos)
            if (res is True):
                Notification.notify(Notificator.onBombGameMoveDir)
                pass
            pass

        with source.addRepeatTask() as (tc_rotate, tc_until):
            tc_rotate.addTask("TaskMouseMoveDistance", Distance=0)
            tc_rotate.addFunction(__SetMoveDir)

            with tc_until.addRaceTask(2) as (tc_until_Dir, tc_until_Click):
                tc_until_Dir.addListener(Notificator.onBombGameMoveDir)

                tc_until_Click.addTask("TaskMouseButtonClick", isDown=False)
                pass
            pass
        source.addTask("AliasBombGameBombRotate", Bomb=self.Bomb)

        pass

    def __PickItem(self, source, slot):
        Item = slot.Item
        Item.PrccoesPick(slot)
        slot.setItemCheckSame(self.BombGame.item_None_Open)
        slot.UpdateTypeVisual()
        pass

    pass
