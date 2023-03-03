from Foundation.Object.DemonObject import DemonObject


class ObjectReagentsButton(DemonObject):
    def _onParams(self, params):
        super(ObjectReagentsButton, self)._onParams(params)
        self.params["EnablePaper"] = params.get("EnablePaper", False)
        pass

    pass
