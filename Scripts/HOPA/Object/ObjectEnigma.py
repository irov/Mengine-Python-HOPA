from Foundation.Object.DemonObject import DemonObject


class ObjectEnigma(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "Play")
        Type.addParam(Type, "Playing")
        Type.addParam(Type, "Skiping")  # Enigma in skip state
        Type.addParam(Type, "Skipped")  # set to True if Enigma was Skipped
        Type.addParam(Type, "EnigmaName")
        Type.addParam(Type, "EnigmaParams")
        Type.addParam(Type, "Pause")
        Type.addParam(Type, "Complete")

    def _onParams(self, params):
        super(ObjectEnigma, self)._onParams(params)

        self.initParam("Play", params, False)
        self.initParam("Playing", params, False)
        self.initParam("Skiping", params, False)
        self.initParam("Skipped", params, False)
        self.initParam("EnigmaName", params, None)
        self.initParam("EnigmaParams", params, None)
        self.initParam("Pause", params, False)
        self.initParam("Complete", params, False)
