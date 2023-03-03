from HOPA.Macro.MacroCommand import MacroCommand


class MacroAchievement(MacroCommand):
    def _onValues(self, values):
        self.AchievementName = values[0]
        pass

    def _onGenerate(self, source):
        if self.AchievementName is None:
            Trace.log("Macro", 0, "MacroAchievement {} not exist".format(self.AchievementName))
            return
            pass

        source.addNotify(Notificator.onAchievementUnlocked, self.AchievementName)
        pass

    pass
