from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinSocket
from HOPA.HintAction import HintAction


class HintActionSocketUseFittingInventoryItem(HintAction, MixinSocket):
    def __init__(self):
        super(HintActionSocketUseFittingInventoryItem, self).__init__()
        pass

    def _onParams(self, params):
        super(HintActionSocketUseFittingInventoryItem, self)._onParams(params)

        self.InventoryItem = params["InventoryItem"]
        pass

    def _getHintObject(self):
        return self.Socket
        pass

    def _onCheck(self):
        Inventory = DemonManager.getDemon("FittingInventory")

        if Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
            pass

        return True
        pass

    def _onAction(self, source, hint):
        Point = hint.getPoint()

        source.addTask("TaskSceneLayerGroupEnable", LayerName="HintEffect", Value=True)

        source.addTask("TaskSoundEffect", SoundName="SparklesCircle", Wait=False)

        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintWay", Value=Point)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintWay", Loop=True, Wait=False)

        P0 = Point

        InventoryItemEntity = self.InventoryItem.getEntity()
        Sprite = InventoryItemEntity.getSprite()

        P2 = Sprite.getWorldImageCenter()

        p1x = P0[0] if P0[1] > P2[1] else P2[0]
        p1y = P2[1] if P0[1] > P2[1] else P0[1]

        P1 = (p1x, p1y)

        source.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName="Movie_HintWay", Point1=P1, To=P2,
                       Speed=600 * 0.001)  # speed fix

        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintInventory", Value=P2)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintInventory", Loop=True, Wait=False)

        NP0 = P2

        SocketEntity = self.Socket.getEntity()
        HotSpot = SocketEntity.getHotSpot()

        NP2 = HotSpot.getWorldPolygonCenter()

        np1x = NP0[0] if NP0[1] > NP2[1] else NP2[0]
        np1y = NP2[1] if NP0[1] > NP2[1] else NP0[1]

        NP1 = (np1x, np1y)

        source.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName="Movie_HintWay", Point1=NP1, To=NP2,
                       Speed=600 * 0.001)  # speed fix
        source.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintWay")

        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintTarget", Value=NP2)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintTarget", Loop=True, Wait=False)

        source.addTask("TaskSoundEffect", SoundName="Sparklesdisappear", Wait=False, Important=False)
        source.addTask("TaskFunction", Fn=self.setEnd)
        pass

    def _onEnd(self):
        self._runEndEffect()

        super(HintActionSocketUseFittingInventoryItem, self)._onEnd()

    def _onEndEffect(self, source):
        source.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintInventory")
        source.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintTarget")

    pass
