from Foundation.Object.DemonObject import DemonObject

class ObjectTicTacToe(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, 'CurrentPlayer')
        Type.addParam(Type, 'Winner')
        Type.addParam(Type, 'PlayerXWins')
        Type.addParam(Type, 'PlayerOWins')
        Type.addParam(Type, 'CellsState')

    def _onParams(self, params):
        super(ObjectTicTacToe, self)._onParams(params)
        self.initParam('CurrentPlayer', params, 'X')
        self.initParam('Winner', params, None)
        self.initParam('PlayerXWins', params, 0)
        self.initParam('PlayerOWins', params, 0)
        self.initParam('CellsState', params, {})