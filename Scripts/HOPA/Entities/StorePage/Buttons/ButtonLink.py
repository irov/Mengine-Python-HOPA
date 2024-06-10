from HOPA.Entities.StorePage.Buttons.ButtonMixin import ButtonMixin


class ButtonLink(ButtonMixin):
    action = "link"

    def getLinkUrl(self):
        return unicode(self.params.link_url, "utf-8")

    def _scopeAction(self, source):
        source.addFunction(Mengine.openUrlInDefaultBrowser, self.getLinkUrl())
