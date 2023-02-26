from Foundation.Task.TaskAlias import TaskAlias

class AliasMultyplMovePlay(TaskAlias):
    def __init__(self):
        super(AliasMultyplMovePlay, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasMultyplMovePlay, self)._onParams(params)
        self.Movies = params.get("Movies")
        pass

    def _onInitialize(self):
        super(AliasMultyplMovePlay, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        if (len(self.Movies) == 0):
            return
            pass

        if (self.Movies[0] == None or len(self.Movies[0]) == 0):
            return
            pass

        tuples = self.Movies[0]

        for movieTuple in tuples:
            if (movieTuple[0] == None):
                continue
                pass
            source.addTask("TaskMoviePlay", Movie=movieTuple[0], Wait=movieTuple[1])
            pass
        pass
    pass