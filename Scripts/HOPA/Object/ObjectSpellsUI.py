from Foundation.Object.DemonObject import DemonObject

class ObjectSpellsUI(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

    def _onParams(self, params):
        super(ObjectSpellsUI, self)._onParams(params)

    def getSpellUIButton(self, spell_type):
        if self.isActive():
            return self.entity.getSpellUIButton(spell_type)