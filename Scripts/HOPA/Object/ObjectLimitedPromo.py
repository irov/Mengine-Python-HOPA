from Foundation.MonetizationManager import MonetizationManager
from Foundation.Object.DemonObject import DemonObject
from HOPA.Entities.LimitedPromo.LimitedPromo import EVENT_TIMEOUT


class ObjectLimitedPromo(DemonObject):
    EVENT_TIMEOUT = EVENT_TIMEOUT

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "EndTimestamps")
        Type.addParam(Type, "ActivatedProducts")

    def _onParams(self, params):
        super(ObjectLimitedPromo, self)._onParams(params)

        self.initParam("EndTimestamps", params, {})
        self.initParam("ActivatedProducts", params, {})

    def run(self, prod_id):
        if self.isActive():
            self.entity.run(prod_id)
            return
        elif _DEVELOPMENT is True:
            Trace.msg_err("LimitedPromo is not active for run()")

        # start offer, it will be displayed when entity activated
        promotion = MonetizationManager.getSpecialPromoById(prod_id)
        EndTimestamps = self.getEndTimestamps()
        if promotion.tag not in EndTimestamps:
            EndTimestamps[promotion.tag] = Mengine.getTimeMs() / 1000 + promotion.limit_delay
            self.setEndTimestamps(EndTimestamps)

    def hasActivePromoNow(self):
        if self.isActive():
            return self.entity.hasActivePromoNow()
        return False

    def getActivePromoNow(self):
        """ returns product id of current promo """
        if self.isActive():
            return self.entity.getActivePromoNow()
        return None

    def setActivatedProduct(self, prod_id):
        ActivatedProducts = self.getActivatedProducts()
        ActivatedProducts[prod_id] = Mengine.getTimeMs() / 1000
        self.setActivatedProducts(ActivatedProducts)

    def isActivated(self, prod_id):
        return prod_id in self.getActivatedProducts()

    def whenActivated(self, prod_id):
        return self.getActivatedProducts().get(prod_id)

    def hasActivePromo(self):
        active_promotions = self.getEndTimestamps()
        if len(active_promotions) > 0:
            return True
        return False

    def endPromoByTag(self, tag):
        EndTimestamps = self.getEndTimestamps()
        if tag in EndTimestamps:
            EndTimestamps.pop(tag)
            self.setEndTimestamps(EndTimestamps)
            return True
        return False

    def endPromoByProductId(self, prod_id):
        params = MonetizationManager.getSpecialPromoById(prod_id)
        return self.endPromoByTag(params.tag)
