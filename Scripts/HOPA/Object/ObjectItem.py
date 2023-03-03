from Foundation.Object.ObjectInteraction import ObjectInteraction


class ObjectItem(ObjectInteraction):
    @staticmethod
    def declareORM(Type):
        ObjectInteraction.declareORM(Type)

        Type.addResource(Type, "SpriteResourceNamePure")
        Type.addResource(Type, "SpriteResourceNameFull")
        Type.addResource(Type, "HotspotImageResourceName")

        Type.addConst(Type, "PureOffset")
        Type.addConst(Type, "PickOffset")

        Type.addParam(Type, "ArrowPoint")
        Type.addParam(Type, "SlotPoint")
        pass

    def _onParams(self, params):
        super(ObjectItem, self)._onParams(params)

        self.initResource("SpriteResourceNamePure", params, None)
        self.initResource("SpriteResourceNameFull", params, None)

        self.initResource("HotspotImageResourceName", params)

        self.initConst("PureOffset", params, (0.0, 0.0))
        self.initConst("PickOffset", params, (0.0, 0.0))
        self.initParam("ArrowPoint", params, (0, 0))
        self.initParam("SlotPoint", params, None)
        pass

    pass
