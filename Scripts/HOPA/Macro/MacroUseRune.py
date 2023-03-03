from HOPA.Macro.MacroCommand import MacroCommand


class MacroUseRune(MacroCommand):
    def _onValues(self, values):
        self.Rune_ID = values[0]
        self.ObjectName = values[1]

        self.Wait = True
        if len(values) > 2:
            self.Wait = bool(values[2])
        pass

    def _onInitialize(self):
        FinderType, self.Object = self.findObject(self.ObjectName)
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "UseRune", SceneName=self.SceneName, GroupName=self.GroupName,
                              Rune_ID=self.Rune_ID, Object=self.Object)

        with Quest as tc_quest:
            tc_quest.addNotify(Notificator.onRuneReady)
            if self.Object.getType() is "ObjectSocket":
                tc_quest.addFunction(self.Object.setInteractive, True)

            if self.Wait:
                tc_quest.addListener(Notificator.onUseRune, Filter=(lambda RuneID, Socket: RuneID is self.Rune_ID))
            else:
                tc_quest.addListener(Notificator.onStartUseRune, Filter=(lambda RuneID, Socket: RuneID is self.Rune_ID))

            if self.Object.getType() is "ObjectSocket":
                tc_quest.addFunction(self.Object.setInteractive, False)

    # def _Set_New_Rune_State(self,source):
    #     source.addNotify(Notificator.onRuneUseReady)
    #     # print "MacroGetRune  _Set_New_Rune ", self.RuneID
    #     # DemonMagicGlove = DemonManager.getDemon('MagicGlove')
    #     # DemonMagicGlove.setParam("State", "Ready")

    pass
