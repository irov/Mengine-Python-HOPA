from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Functor import Functor
from HOPA.TipManager import TipManager


class TipItem(BaseEntity):
    # TIME_TIP = 0.1
    TIME_TIP = 0.1 * 1000  # speed fix

    TIP_SHOW = 1
    TIP_HIDE = 2

    TIP_OFFSET = 10

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "TipItem", Update=TipItem.__restoreTipItem)
        Type.addAction(Type, "TipItemID", Update=TipItem.__updateTipItemID)
        pass

    def __init__(self):
        super(TipItem, self).__init__()

        self.sprite = None

        self.defaultPoint = (0, 100)
        self.status = TipItem.TIP_HIDE
        self.text = None
        self.TipHeight = 50
        self.arrowSprite = None
        pass

    def _onRestore(self):
        spriteTip = self.object.getObject("Sprite_TipItem")
        spriteEntity = spriteTip.getEntity()
        self.sprite = spriteEntity.getSprite()
        self.sprite.disable()
        self.text = self.object.getObject("Text_Message")
        pass

    def _onActivate(self):
        pass

    def _onDeactivate(self):
        if TaskManager.existTaskChain("TipItemPlay") is True:
            TaskManager.cancelTaskChain("TipItemPlay")
            pass
        pass

    def tipShow(self, TipItemID, delayTime, cb):
        #        print "Tip.tipShow"
        #        print "status = ", self.status
        #        print "::::::::"
        if self.status is TipItem.TIP_SHOW:
            self.releaseTip()
            pass

        self.status = TipItem.TIP_SHOW
        self.object.setParam("TipItemID", TipItemID)

        resolution = Mengine.getContentResolution()
        width = resolution.getWidth()
        height = resolution.getHeight()

        textEntity = self.text.getEntity()
        textField = textEntity.getTextField()
        textLength = textField.getLength()
        #        print "textLength ", textLength
        textPosition = self.text.getParam("Position")
        #        print "textPosition ", textPosition

        arrowScreenPosition = Mengine.getCursorPosition()
        #        arrowSprite = ArrowManager.getSprite()
        #        arrowOrigin = ArrowManager.getCursorOrigin()
        #        arrowSize = arrowSprite.getImageSize()
        arrowSizeX = 32
        arrowSizeY = 32
        arrowOriginX = 0
        arrowOriginY = 0

        arrowPosition = (arrowScreenPosition.x, arrowScreenPosition.y)

        #        print "arrowPosiiton, arrowOrigin, arrowSize ", arrowPosition, arrowOrigin, arrowSize

        if self.arrowSprite is None:
            pass

        spriteSize = self.sprite.getSurfaceSize()

        #        print "SpriteSize before ", spriteSize

        scaleWidth = (textLength.x + TipItem.TIP_OFFSET) / spriteSize.x
        scaleHeight = (textLength.y + TipItem.TIP_OFFSET) / spriteSize.y

        self.sprite.setScale((scaleWidth, scaleHeight, 1.0))

        spriteWidth = scaleWidth * spriteSize.x
        spriteHeight = scaleHeight * spriteSize.y

        TipPoint = (arrowPosition[0] + arrowSizeX - arrowOriginX, arrowPosition[1] + arrowSizeY - arrowOriginY)
        #        print "Tips Parameters"
        #        print "TextLength.x ", textLength.x
        #        print "spriteWidth ", spriteWidth
        #        print "arrowPosition.x ", arrowPosition[0]
        #        print "width", width
        #        print "(spriteWidth + arrowPosition[0])>width: ", (spriteWidth + arrowPosition[0]), " > ", width
        if (spriteWidth + TipPoint[0]) > width:
            TipPoint = (arrowPosition[0] - spriteWidth, TipPoint[1])
            pass

        #        print "Tips Parameters"
        #        print "TextLength.y ", textLength.y
        #        print "scaleHeight ", scaleHeight
        #        print "arrowPosition.y ", arrowPosition[1]
        #        print "height", height
        #        print "(spriteHeight + arrowPosition[1])>height: ", (spriteHeight + arrowPosition[1]), " > ", height

        if (spriteHeight + TipPoint[1]) > height:
            TipPoint = (TipPoint[0], arrowPosition[1] - spriteHeight)
            pass

        #        print TipPoint
        self.sprite.setLocalPosition(TipPoint)
        Position = (
            TipPoint[0] + spriteSize.x * scaleWidth / 2,
            TipPoint[1] + spriteSize.y * scaleHeight / 2 - textLength.y / 2
        )
        self.text.setParam("Position", Position)

        textEntity.setLocalAlpha(0.0)
        textEntity.enable()

        self.sprite.setLocalAlpha(0.0)
        self.sprite.enable()

        self.sprite.colorStop()

        with TaskManager.createTaskChain(Name="TipItemPlay", Group=self.object,
                                         Cb=Functor(self._onTipEndComplete, cb)) as tc:
            with tc.addRaceTask(2) as (tc_show, tc_skip):
                tc_show.addTask("TaskDelay", Time=delayTime)

                with tc_show.addParallelTask(2) as (tc_show_0, tc_show_1):
                    tc_show_0.addTask("TaskNodeAlphaTo", Node=self.sprite, Time=TipItem.TIME_TIP, To=1.0)
                    tc_show_1.addTask("TaskNodeAlphaTo", Node=textEntity, Time=TipItem.TIME_TIP, To=1.0)
                    pass
                #                tc_show.addTask( "TaskEnable", Object = self.text)
                tc_show.addTask("TaskListener", ID=Notificator.onInventorySlotItemLeave)
                tc_show.addTask("TaskEnable", Object=self.text, Value=False)
                tc_show.addTask("TaskNodeEnable", Node=self.sprite, Value=False)

                tc_skip.addTask("TaskListener", ID=Notificator.onInventorySlotItemLeave)
                tc_skip.addTask("TaskEnable", Object=self.text, Value=False)
                tc_skip.addTask("TaskNodeEnable", Node=self.sprite, Value=False)
            pass
        pass

    def _onTipEndComplete(self, isSkip, cb):
        self.status = TipItem.TIP_HIDE

        if isSkip is True:
            return

        cb(self.object)
        pass

    def __restoreTipItem(self, tipItem):
        pass

    def __updateTipItemID(self, tipItemID):
        if tipItemID is not None:
            TipTextID = TipManager.getTextID(tipItemID)
            self.text.setParams(TextID=TipTextID)
            self.text.setParams(Enable=False)
            pass
        pass

    def releaseTip(self):
        self.status = TipItem.TIP_HIDE
