from Foundation.Task.TaskAlias import TaskAlias

class AliasCombatSpellAiTurn(TaskAlias):
    def __init__(self):
        super(AliasCombatSpellAiTurn, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasCombatSpellAiTurn, self)._onParams(params)
        self.CombatSpell = params.get("CombatSpell")
        pass

    def _onInitialize(self):
        super(AliasCombatSpellAiTurn, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        result = self.CombatSpell.TurnAi()
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
            posEat = result[0]
            posMove = result[1]

            # slotMove = self.CombatSpell.getSlot(posMove)
            slotEat = self.CombatSpell.getSlot(posEat)

            # movieMove = self.CombatSpell.getAiMoveAnimation(result)
            movieEat = self.CombatSpell.getAiEatAnimation(result)

            source.addTask("TaskFunction", Fn=attachMovie, Args=(slotEat, movieEat))
            source.addTask("TaskMoviePlay", Movie=movieEat, Wait=True)
            source.addTask("TaskFunction", Fn=dettachMovie, Args=(slotEat,))

            # source.addTask("TaskFunction", Fn = attachMovie, Args = (slotMove, movieMove))
            # source.addTask("TaskMoviePlay", Movie = movieMove, Wait = True)
            # source.addTask("TaskFunction", Fn = dettachMovie, Args = (slotMove,))

            pass
        else:  # move
            posMove = result[0]

            slotMove = self.CombatSpell.getSlot(posMove)

            movieMove = self.CombatSpell.getAiMoveAnimation(result)

            source.addTask("TaskFunction", Fn=attachMovie, Args=(slotMove, movieMove))
            source.addTask("TaskMoviePlay", Movie=movieMove, Wait=True)
            source.addTask("TaskFunction", Fn=dettachMovie, Args=(slotMove,))

            pass

        source.addTask("TaskFunction", Fn=update)

        pass
    pass