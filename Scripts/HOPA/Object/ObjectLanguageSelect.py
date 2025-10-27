from Foundation.Object.DemonObject import DemonObject


class ObjectLanguageSelect(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam("bPrevLangSetted")
        Type.declareParam("PrevLanguage")

    def _onParams(self, params):
        super(ObjectLanguageSelect, self)._onParams(params)
        self.initParam("bPrevLangSetted", params, False)
        self.initParam("PrevLanguage", params, str())
