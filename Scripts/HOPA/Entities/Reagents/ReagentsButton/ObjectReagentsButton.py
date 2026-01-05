from Foundation.Object.DemonObject import DemonObject


class ObjectReagentsButton(DemonObject):
    def _onParams(self, params):
        super(ObjectReagentsButton, self)._onParams(params)

        self.initParam("EnablePaper", params, False)
        pass

    pass
