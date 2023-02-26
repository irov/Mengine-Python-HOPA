from Foundation.Task.TaskAlias import TaskAlias

class AliasCombatSpellPlayerTurn(TaskAlias):
    def __init__(self):
        super(AliasCombatSpellPlayerTurn, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasCombatSpellPlayerTurn, self)._onParams(params)
        self.CombatSpell = params.get("CombatSpell")
        pass

    def _onInitialize(self):
        super(AliasCombatSpellPlayerTurn, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        result = self.CombatSpell.TurnPlayer()

        if (result is None):
            return

        def update():
            self.CombatSpell.UpdateVisual()
            pass

        def attachMovie(slot, Movie):
            slot.AttachMovie(Movie)
            pass

        def dettachMovie(slot):
            slot.DettachMovie()
            pass

        if (len(result) == 4):  # eat
            posEat = result[3]

            slotEat = self.CombatSpell.getSlot(posEat)

            movieEat = self.CombatSpell.Movie_PlayerEat

            source.addTask("TaskFunction", Fn=attachMovie, Args=(slotEat, movieEat))
            source.addTask("TaskMoviePlay", Movie=movieEat, Wait=True)
            source.addTask("TaskFunction", Fn=dettachMovie, Args=(slotEat,))
            pass
        else:  # move
            posMove = result[0]

            slotMove = self.CombatSpell.getSlot(posMove)

            movieMove = self.CombatSpell.Movie_PlayerMove

            source.addTask("TaskFunction", Fn=attachMovie, Args=(slotMove, movieMove))
            source.addTask("TaskMoviePlay", Movie=movieMove, Wait=True)
            source.addTask("TaskFunction", Fn=dettachMovie, Args=(slotMove,))

            pass

        source.addTask("TaskFunction", Fn=update)
        pass
    pass