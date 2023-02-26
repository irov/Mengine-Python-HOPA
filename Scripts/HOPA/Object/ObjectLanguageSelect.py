from Foundation.Object.DemonObject import DemonObject

class ObjectLanguageSelect(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, "bPrevLangSetted")
        Type.addParam(Type, "PrevLanguage")

    def _onParams(self, params):
        super(ObjectLanguageSelect, self)._onParams(params)
        self.initParam("bPrevLangSetted", params, False)
        self.initParam("PrevLanguage", params, str())