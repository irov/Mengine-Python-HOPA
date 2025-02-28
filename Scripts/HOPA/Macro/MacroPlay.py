from HOPA.Macro.MacroCommand import MacroCommand


class MacroPlay(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = values[0]

        self.SubMovieName = values[1] if len(values) > 1 else None
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            Filter = ["ObjectMovie", "ObjectEffect", "ObjectAnimation", "ObjectVideo", "ObjectMovie2"]

            if self.hasObject(self.ObjectName, Filter) is False:
                self.initializeFailed("MacroPlay not found Object %s in group %s" % (self.ObjectName, self.GroupName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        # source.addTask("TaskPrint", Value = "MacroPlay")
        FinderType, Object = self.findObject(self.ObjectName)
        ObjectType = Object.getType()

        Quest = self.addQuest(source, "Play", SceneName=self.SceneName, GroupName=self.GroupName, Object=Object)

        with Quest as tc_quest:
            if ObjectType == "ObjectMovie":
                if self.SubMovieName is None:
                    Wait = Object.getLoop() is False

                    tc_quest.addTask("TaskMoviePlay", Movie=Object, Wait=Wait, ValidationGroupEnable=False)
                else:
                    # def _cb(movie):
                    #     submovie = movie.getEntity().getSubMovie(self.SubMovieName)
                    #     submovie.play()
                    #
                    # tc_quest.addFunction(_cb, Object)

                    tc_quest.addTask("TaskSubMoviePlay", Movie=Object, SubMovieName=self.SubMovieName)
                pass
            elif ObjectType == "ObjectVideo":
                Wait = Object.getLoop() is False

                tc_quest.addTask("TaskVideoPlay", Video=Object, Wait=Wait)
                pass
            elif ObjectType == "ObjectAnimation":
                Wait = Object.getLoop() is False

                tc_quest.addTask("TaskAnimationPlay", Animation=Object, Wait=Wait, ValidationGroupEnable=False)
                pass
            elif ObjectType == "ObjectMovie2":
                Wait = Object.getLoop() is False
                if self.SubMovieName is None:
                    Wait = Object.getLoop() is False

                    tc_quest.addTask("TaskAnimationPlay", Animation=Object, Wait=Wait, ValidationGroupEnable=False)
                else:
                    # def _cb(movie):
                    #     submovie = movie.getEntity().getSubMovie(self.SubMovieName)
                    #     submovie.play()
                    #
                    # tc_quest.addFunction(_cb, Object)

                    tc_quest.addTask("TaskSubMovie2Play", Movie2=Object, SubMovie2Name=self.SubMovieName)

                pass
            else:
                Trace.log("Macro", 0, "MacroPlay._onGenerate type %s not support Group %s Index %d" % (
                ObjectType, self.GroupName, self.Index))

                tc_quest.addDummy()
                pass

            pass
        # if ObjectType == "ObjectMovie":
        #     Wait = Object.getLoop() is False
        #
        #     # source.addTask("TaskMovieRewind", Movie = Object)
        #     source.addTask("TaskMoviePlay", Movie = Object, Wait = Wait, ValidationGroupEnable = False)
        #     pass
        # elif ObjectType == "ObjectVideo":
        #     Wait = Object.getLoop() is False
        #
        #     source.addTask("TaskVideoPlay", Video = Object, Wait = Wait)
        #     pass
        # elif ObjectType == "ObjectAnimation":
        #     Wait = Object.getLoop() is False
        #
        #     source.addTask("TaskAnimationPlay", Animation = Object, Wait = Wait, ValidationGroupEnable = False)
        #     pass
        # else:
        #     Trace.log("Macro", 0, "MacroPlay._onGenerate type %s not support Group %s Index %d"%(ObjectType, self.GroupName, self.Index))
        #     pass

        pass

    pass
