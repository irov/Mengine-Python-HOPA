from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Utils import getCurrentPublisher
from HOPA.Entities.Monetization.BaseComponent import BaseComponent


class Guides(BaseComponent):
    _settings = {
        "is_enable": "EnablePaidGuides",
        "product_id": "GuidesProductID",
        "movie": "GuidesButton",
    }
    _defaults = {
        "product_id": "tech_guides",
        "movie": "Movie2Button_{}".format(getCurrentPublisher()),
        "group": "GuideOpen",
    }

    def _createParams(self):
        self.default_movie_name = "Movie2Button_Guide"

    def _check(self):
        if self.group is None:
            self._error("Not found group {!r}".format(self.group_name))
            return False
        if self.group.hasObject(self.movie_name) is False:
            self.movie_name = self.default_movie_name  # use default button
            if MonetizationManager.getGeneralSetting(self._settings["movie"], None) is not None:
                # if we add setting for another movie - raise error, but run component anyway
                self._error("Not found movie {!r} in group {!r}".format(self.movie_name, self.group_name))
        if MonetizationManager.getGeneralSetting("GameStoreName", "GameStore") == "GameStore":
            if DemonManager.hasDemon("SpecialPromotion") is False:
                self._error("Demon 'SpecialPromotion' not found")
                return False
        return True

    def _toggleButton(self):
        buttons = [movie for movie in self.group.getObjects() if movie.getName().startswith("Movie2Button_")]

        # enable only one button
        for button in buttons:
            if button.getName() == self.movie_name:
                button.setEnable(True)
                continue
            button.setEnable(False)

    def _run(self):
        PolicyManager.setPolicy("GuideOpen", "PolicyGuideOpenPaid")

        self.addObserver(Notificator.onStageInit, self._cbStageRun)
        self.addObserver(Notificator.onStageLoad, self._cbStageRun)

    def _cbStageRun(self, stage):
        self._toggleButton()
        return False
