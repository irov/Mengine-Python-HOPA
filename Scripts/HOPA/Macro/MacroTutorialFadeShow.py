from HOPA.Macro.MacroCommand import MacroCommand


class MacroTutorialFadeShow(MacroCommand):

    def _onValues(self, values):
        self.MovieID = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onTutorialFadeShow, self.MovieID)
        source.addListener(Notificator.onTutorialFadeShowEnd, Filter=lambda movie_id: movie_id == self.MovieID)
        pass
