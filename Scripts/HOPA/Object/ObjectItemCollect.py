from Foundation.Object.DemonObject import DemonObject


class ObjectItemCollect(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam('ItemCollectArea')
        Type.declareParam('ItemsList')
        # Type.declareParam('AreasCenter')
        Type.declareParam('Radius')
        Type.declareParam('DeviationAngle')
        Type.declareParam('AttachItem')
        Type.declareParam('PreAttach')

    def _onParams(self, params):
        super(ObjectItemCollect, self)._onParams(params)
        self.initParam('ItemCollectArea', params, None)
        self.initParam('ItemsList', params, [])
        # self.initParam('AreasCenter', params, ())
        self.initParam('Radius', params, 0)
        self.initParam('DeviationAngle', params, 0)
        self.initParam('AttachItem', params, '')
        self.initParam('PreAttach', params, None)

    def scopePlaySceneEffect(self, source, flag):
        if self.entity.isActivate():
            source.addScope(self.entity.playSceneEffect, flag)
        else:
            if _DEVELOPMENT is True:
                Trace.log("Entity", 0, "Entity ItemCollect is not activate to run playSceneEffect")
            source.addDummy()

    def getOpeningProcessProgress(self):
        if self.isActive():
            return self.entity.getOpeningProcessProgress()

    def cancelTaskChain(self):
        if self.entity.tc is not None:
            self.entity.tc.cancel()
        self.entity.tc = None

    def playItemSelectEffect(self, item):
        if self.isActive():
            self.entity.playItemSelectEffect(item)
