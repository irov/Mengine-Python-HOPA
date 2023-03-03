from Foundation.Entity.BaseEntity import BaseEntity

from CollectedMapManager import CollectedMapManager


class CollectedMap(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate(Type, "OpenParts")
        pass

    def _onPreparation(self):
        super(CollectedMap, self)._onPreparation()
        Data = CollectedMapManager.getData(self.object)
        for partID, object in Data.iteritems():
            if partID not in self.OpenParts:
                object.setEnable(False)
                pass
            else:
                object.setEnable(True)
                pass
            pass
        pass

    def _onActivate(self):
        super(CollectedMap, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(CollectedMap, self)._onDeactivate()
        pass

    pass
