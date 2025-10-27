from Foundation.Object.DemonObject import DemonObject


class ObjectEnigma(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Play")
        Type.declareParam("Playing")
        Type.declareParam("Skiping")  # Enigma in skip state
        Type.declareParam("Skipped")  # set to True if Enigma was Skipped
        Type.declareParam("EnigmaName")
        Type.declareParam("EnigmaParams")
        Type.declareParam("Pause")
        Type.declareParam("Complete")

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
