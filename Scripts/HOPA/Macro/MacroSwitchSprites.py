from HOPA.Macro.MacroCommand import MacroCommand

class MacroSwitchSprites(MacroCommand):
    def _onValues(self, values):
        if _DEVELOPMENT is True:
            if len(values) == 0:
                msg = "Macro {mc.CommandType} not add any param, group {mc.GroupName}:{mc.Index}".format(mc=self)
                self.initializeFalied(msg)

            if len(values) < 3:
                msg = "Macro {mc.CommandType} not add enough params, group {mc.GroupName}:{mc.Index}".format(mc=self)
                self.initializeFailed(msg)

        self.Sprite1 = values[0]
        self.Sprites = []
        for i in range(1, len(values) - 1):
            self.Sprites.append(values[i])

        # self.Sprite2 = values[1]
        time = values[-1]  # time in seconds

        try:
            self.Time = float(time) * 1000.0
        except ValueError:
            msg = "Macro {mc.CommandType} could not convert time param to float, group {mc.GroupName}:{mc.Index}".format(mc=self)
            self.initializeFailed(msg)
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            Sprite1_FinderType, Sprite1_Object = self.findObject(self.Sprite1)

            if Sprite1_Object is None:
                msg = "Macro {mc.CommandType} not found Object {mc.Sprite1} in group {mc.GroupName}".format(mc=self)
                self.initializeFailed(msg)

            for elem in self.Sprites:
                Sprite2_FinderType, Sprite2_Object = self.findObject(elem)

                if Sprite2_Object is None:
                    msg = "Macro {mc.CommandType} not found Object {mc2}, type={mc3} in group {mc.GroupName}".format(mc=self, mc2=elem.getName(), mc3=Sprite2_FinderType)
                    self.initializeFailed(msg)
                pass
            pass

    def _onGenerate(self, source):
        Sprite1_FinderType, Sprite1_Object = self.findObject(self.Sprite1)
        Sprite_Objects = []
        for elem in self.Sprites:
            Sprite2_FinderType, Sprite2_Object = self.findObject(elem)
            Sprite_Objects.append(Sprite2_Object)

        with source.addParallelTask(2) as (source_hide, source_show):
            source_hide.addTask("AliasObjectAlphaTo", Object=Sprite1_Object, From=1.0, To=0.0, Time=self.Time)
            for Sprite, source_list in source_show.addParallelTaskList(Sprite_Objects):
                source_list.addEnable(Sprite)
                source_list.addTask("AliasObjectAlphaTo", Object=Sprite, From=0.0, To=1.0, Time=self.Time)

        source.addDisable(Sprite1_Object)

        source.addTask("TaskObjectSetAlpha", Object=Sprite1_Object, Value=1.0)

        pass