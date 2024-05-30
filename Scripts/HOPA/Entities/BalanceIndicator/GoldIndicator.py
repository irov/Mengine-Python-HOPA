from HOPA.Entities.BalanceIndicator.IndicatorMixin import IndicatorMixin


class GoldIndicator(IndicatorMixin):
    type = "Gold"
    icon_tag = "Coin"
    text_alias = "$AliasGoldBalance"
    text_id = "ID_TEXT_GOLD_BALANCE"
    identity = Notificator.onUpdateGoldBalance
