from Foundation.SystemManager import SystemManager
from HOPA.Entities.StorePage.Buttons.ButtonMixin import ButtonMixin


class ButtonAdvert(ButtonMixin):
    aliases = {
        "title": "$AliasStoreButtonTitle",
        "descr": "$AliasStoreButtonDescr",
        "gold": "$AliasStoreGoldReward",
        "energy": "$AliasStoreEnergyReward",
        "reset_timer": "$AliasStoreAdvertTimer",
        "ads_counter": "$AliasStoreAdvertCounter"
    }
    action = "advert"

    # Texts

    def _getAliasAndTextID(self):
        alias_param = {
            self.aliases["title"]: self.params.title_text_id,
            self.aliases["descr"]: self.params.descr_text_id,
            self.aliases["gold"]: self.params.gold_reward_text_id,
            self.aliases["energy"]: self.params.energy_reward_text_id,
            self.aliases["reset_timer"]: self.params.timer_text_id,
            self.aliases["ads_counter"]: self.params.counter_text_id,
        }
        return alias_param

    def setText(self):
        reward = self.product_params.reward
        if reward is not None:
            self.setTextArguments("gold", reward.get("Gold", 0))
            self.setTextArguments("energy", reward.get("Energy", 0))
        self.setTextArguments("reset_timer", "")
        self.setTextArguments("ads_counter", 0, 0)

    # States

    def hasNotify(self):
        if SystemManager.hasSystem("SystemMonetization") is True:
            SystemMonetization = SystemManager.getSystem("SystemMonetization")
            if SystemMonetization.isAdsEnded(self.getAdvertName()) is False:
                return True
        return False

    def updateTimer(self, *args):
        self.setTextArguments("reset_timer", *args)

    def updateCounter(self, current, maximum):
        self.setTextArguments("ads_counter", current, maximum)

    def getAdvertName(self):
        return self.product_params.name

    # Scopes

    def _scopeAction(self, source):
        source.addTask("AliasShowAdvert", AdType="Rewarded", AdUnitName=self.getAdvertName())
