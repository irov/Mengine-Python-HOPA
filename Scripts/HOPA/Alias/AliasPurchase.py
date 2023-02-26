from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasPurchase(TaskAlias):

    def _onParams(self, params):
        self.Product = params.get("Product")
        self.ProductID = params.get("ProductID")

        if self.Product is None:
            if self.ProductID is None:
                Trace.log("Task", 0, "AliasPurchase params failed - set Product or ProductID")
                return False

            self.Product = MonetizationManager.getProductInfo(self.ProductID)

    def _onInitialize(self):
        if isinstance(self.Product, MonetizationManager.ProductInfoParam) is False:
            self.initializeFailed("AliasPurchase product wrong type {} != MonetizationManager.ProductInfoParam".format(type(self.Product)))

    def _onGenerate(self, source):
        PolicyPurchase = PolicyManager.getPolicy("Purchase", "PolicyPurchaseDummy")
        source.addTask(PolicyPurchase, Product=self.Product)