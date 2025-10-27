from Foundation.Object.ObjectInteraction import ObjectInteraction


class ObjectItem(ObjectInteraction):
    @staticmethod
    def declareORM(Type):
        ObjectInteraction.declareORM(Type)

        Type.declareResource("SpriteResourceNamePure")
        Type.declareResource("SpriteResourceNameFull")
        Type.declareResource("HotspotImageResourceName")

        Type.declareConst("PureOffset")
        Type.declareConst("PickOffset")

        Type.declareParam("ArrowPoint")
        Type.declareParam("SlotPoint")
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
