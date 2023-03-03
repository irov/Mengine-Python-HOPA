from Foundation.Task.TaskAlias import TaskAlias


class AliasDialogSwitchAvatar(TaskAlias):
    def _onParams(self, params):
        super(AliasDialogSwitchAvatar, self)._onParams(params)

        self.Dialog = params.get("Dialog")
        self.DialogPersGroup = params.get("DialogPersGroup", self.Dialog)
        self.CharacterID = params.get("CharacterID")
        self.IdleID = params.get("IdleID")
        self.Wait = params.get("Wait", True)
        pass

    def _onInitialize(self):
        super(AliasDialogSwitchAvatar, self)._onInitialize()

        if self.DialogPersGroup.hasObject("Demon_Switch_Avatar") is False:
            return
            pass

        if _DEVELOPMENT is True:
            if self.CharacterID is None:
                self.initializeFailed("Dialog not setup CharacterID")
                pass

            Demon_Switch_Avatar = self.DialogPersGroup.getObject("Demon_Switch_Avatar")
            Avatar = Demon_Switch_Avatar.findSwitch(self.CharacterID)

            if Avatar is None:
                self.initializeFailed("Dialog not found %s Avatar" % (self.CharacterID))
                pass
        pass

    def _onGenerate(self, source):
        if self.DialogPersGroup.hasObject("Demon_Switch_Avatar") is False:
            return

        Demon_Switch_Avatar = self.DialogPersGroup.getObject("Demon_Switch_Avatar")

        source.addTask("TaskSetParam", Object=Demon_Switch_Avatar, Param="Switch", Value=self.CharacterID)

        Character = Demon_Switch_Avatar.findSwitch(self.CharacterID)

        CharacterType = Character.getType()

        if CharacterType == "ObjectMovie2":
            if self.Wait is True:
                with source.addRaceTask(2) as (tc_movie, tc_complete):
                    with tc_movie.addParallelTask(2) as (tc_play, tc_socket):
                        tc_socket.addScope(self.scope_SubmoviePlay, Character)
                        tc_play.addTask("TaskMovie2Play", Movie2=Character, Wait=True)

                    def __isDialog(Dialog):
                        if self.Dialog is not Dialog:
                            return False
                            pass

                        return True
                        pass

                    tc_complete.addTask("TaskListener", ID=Notificator.onDialogMessageComplete, Filter=__isDialog)
                    pass
                pass
            else:
                with source.addRaceTask(2) as (tc_skip, tc_play_movie):
                    with tc_play_movie.addParallelTask(2) as (tc_play, tc_socket):
                        tc_socket.addScope(self.scope_SubmoviePlay, Character)
                        tc_play.addTask("TaskMovie2Play", Movie2=Character, Wait=True)

                    tc_skip.addTask("TaskMouseButtonClick", isDown=False)
                pass
            pass
        if CharacterType == "ObjectMovie":
            if self.Wait is True:
                with source.addRaceTask(2) as (tc_movie, tc_complete):
                    tc_movie.addTask("TaskMoviePlay", Movie=Character, Wait=True)

                    def __isDialog(Dialog):
                        if self.Dialog is not Dialog:
                            return False
                            pass

                        return True
                        pass

                    tc_complete.addTask("TaskListener", ID=Notificator.onDialogMessageComplete, Filter=__isDialog)
                    pass
                pass
            else:
                with source.addRaceTask(2) as (tc_skip, tc_play_movie):
                    tc_play_movie.addTask("TaskMoviePlay", Movie=Character, Wait=True)
                    tc_skip.addTask("TaskMouseButtonClick", isDown=False)
                pass
            pass

        if self.IdleID is not None:
            Idle = Demon_Switch_Avatar.findSwitch(self.IdleID)

            IdleType = Idle.getType()
            if IdleType == "ObjectMovie2":
                source.addTask("TaskSetParam", Object=Demon_Switch_Avatar, Param="Switch", Value=self.IdleID)

                source.addTask("TaskMovie2Play", Movie2=Idle, Loop=True, Wait=True)

            elif IdleType == "ObjectMovie":
                source.addTask("TaskSetParam", Object=Demon_Switch_Avatar, Param="Switch", Value=self.IdleID)

                source.addTask("TaskMoviePlay", Movie=Idle, Loop=True, Wait=True)
                pass
            pass
        pass

    pass

    def scope_SubmoviePlay(self, tc_skip_socket, Movie):
        if Movie != None:
            if Movie.getEntity().hasSubMovie('SubMuvieDIalog') is True:
                tc_skip_socket.addTask("TaskSocketClick", SocketName="Socket_DialogSkip")
                tc_skip_socket.addTask("TaskSubMovie2Play", Movie2=Movie, SubMovie2Name="SubMuvieDIalog")
        else:
            pass
