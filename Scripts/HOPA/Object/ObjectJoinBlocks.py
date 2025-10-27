from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectJoinBlocks(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("BlockSave")
        pass

    def _onParams(self, params):
        super(ObjectJoinBlocks, self)._onParams(params)

        self.initParam("BlockSave", params, {})
        pass

    pass
