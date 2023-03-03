from Foundation.Task.TaskAlias import TaskAlias


class AliasMultyplMovePlay(TaskAlias):

    def _onParams(self, params):
        super(AliasMultyplMovePlay, self)._onParams(params)
        self.Movies = params.get("Movies")

    def _onGenerate(self, source):
        if len(self.Movies) == 0:
            return

        if self.Movies[0] == None or len(self.Movies[0]) == 0:
            return

        tuples = self.Movies[0]

        for movieTuple in tuples:
            if movieTuple[0] == None:
                continue
            source.addTask("TaskMoviePlay", Movie=movieTuple[0], Wait=movieTuple[1])
