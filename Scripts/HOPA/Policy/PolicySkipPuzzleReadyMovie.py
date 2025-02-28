from Foundation.Task.TaskAlias import TaskAlias


class PolicySkipPuzzleReadyMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicySkipPuzzleReadyMovie, self)._onParams(params)
        # self.SkipPuzzle = DemonManager.getDemon("SkipPuzzle")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskMoviePlay", MovieName="Movie_Ready", Loop=True, Wait=False)
        with source.addRaceTask(2) as (tc_click, tc_skip):
            tc_click.addTask("TaskButtonClick", ButtonName="Button_Skip")
            tc_skip.addListener(Notificator.onEnigmaSkip)
            pass
        source.addTask("TaskMovieStop", MovieName="Movie_Ready")
        pass

    pass
