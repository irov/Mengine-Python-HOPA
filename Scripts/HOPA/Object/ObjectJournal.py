from Foundation.Object.DemonObject import DemonObject


class ObjectJournal(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Pages")
        Type.declareParam("CurrentPage")
        pass

    def _onParams(self, params):
        super(ObjectJournal, self)._onParams(params)
        self.initParam("Pages", params, [])
        self.initParam("CurrentPage", params, None)
        pass

    def hasPage(self, page_id):
        return page_id in self.getPages()

    pass
