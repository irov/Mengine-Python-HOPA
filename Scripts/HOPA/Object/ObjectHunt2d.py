from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectHunt2d(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

    def _onParams(self, params):
        super(ObjectHunt2d, self)._onParams(params)