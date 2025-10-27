from Foundation.Object.DemonObject import DemonObject
from HOPA.Entities.GameStore.GameStore import GameStore


class ObjectGameStore(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("UnblockAdTimestamp")

    def _onParams(self, params):
        super(ObjectGameStore, self)._onParams(params)

        self.initParam("UnblockAdTimestamp", params, None)

    def isStoreEnable(self):
        # use imported method because self.entity may be None
        return GameStore.isStoreEnable()

    def open(self, **kwargs):
        if self.isActive():
            self.entity.openFromAnywhere()

    def generateIcon(self, object_name, prototype_name, env="GeneratedIcon", **params):
        icon = self.generateObjectUnique(object_name, prototype_name, **params)
        icon.setTextAliasEnvironment(env)
        Mengine.setTextAlias(env, "$AliasCoinUsePrice", "ID_EMPTY")
        return icon
