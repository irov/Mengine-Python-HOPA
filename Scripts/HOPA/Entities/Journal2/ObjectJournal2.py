from Foundation.Object.DemonObject import DemonObject


class ObjectJournal2(DemonObject):
    def _onParams(self, params):
        super(ObjectJournal2, self)._onParams(params)
        self.initParam("OpenPages", params, [])
        self.initParam("CurrentIndex", params, 0)
        self.initParam("PageSize", params, 2)
        pass

    pass
