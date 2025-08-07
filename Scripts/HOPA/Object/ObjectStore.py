from Foundation.Object.DemonObject import DemonObject
from Foundation.SceneManager import SceneManager
from HOPA.TransitionManager import TransitionManager


class ObjectStore(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, 'CurrentPageID')
        Type.addParam(Type, 'HiddenPagesID')
        Type.addParam(Type, 'UnvisitedPagesID')

    def _onParams(self, params):
        super(ObjectStore, self)._onParams(params)
        self.initParam('CurrentPageID', params, None)
        self.initParam('HiddenPagesID', params, None)  # initial value - then it would be list
        self.initParam('UnvisitedPagesID', params, None)  # initial value - then it would be list

    # --- methods used in SystemMonetization ---------------------------------------------------------------------------

    def isStoreEnable(self):
        return True

    def open(self, page_id=None):
        if page_id is not None:
            self.setParam("CurrentPageID", page_id)
        if SceneManager.getCurrentSceneName() != "Store":
            TransitionManager.changeScene("Store")

    def generateIcon(self, object_name, prototype_name, env="GeneratedIcon", **params):
        icon = self.generateObjectUnique(object_name, prototype_name, EntityHierarchy=False, **params)
        icon.setTextAliasEnvironment(env)
        Mengine.setTextAlias(env, "$AliasCoinUsePrice", "ID_EMPTY")
        return icon
