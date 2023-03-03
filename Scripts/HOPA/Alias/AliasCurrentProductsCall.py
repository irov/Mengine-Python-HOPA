from Foundation.MonetizationManager import MonetizationManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasCurrentProductsCall(TaskAlias):

    def _onParams(self, params):
        super(AliasCurrentProductsCall, self)._onParams(params)

        self.CallFunction = params["CallFunction"]
        self.Products = MonetizationManager.getProductsInfo()

    def _onInitialize(self):
        if callable(self.CallFunction) is False:
            self.initializeFailed("CallFunction {!r} is not callable [callable {}]".format(self.CallFunction, callable(self.CallFunction)))

    def _onGenerate(self, source):
        prod_ids = self.Products.keys()

        source.addFunction(self.CallFunction, prod_ids)
