from HOPA.Macro.MacroCommand import MacroCommand

class MacroFX(MacroCommand):
    def _onValues(self, values):
        self.SoundName = values[0]

        self.SoundName = self.SoundName
        pass

    def _onInitialize(self):
        if Mengine.hasSound(self.SoundName) is False:
            Trace.log("Command", 0, "!!!!!!!!!!Sound %s not found" % (self.SoundName))
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSoundEffect", SoundName=self.SoundName, Wait=False)
        pass
    pass