from Foundation.Task.TaskAlias import TaskAlias

class PolicyBlackBarPlayStaticWithMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyBlackBarPlayStaticWithMovie, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.Time = params.get("Time")
        self.Movie = params.get("Movie")
        pass

    def _onGenerate(self, source):
        with source.addParallelTask(2) as (tc_text, tc_movie):
            tc_text.addTask("TaskTextSetTextID", TextName="Text_Message", Value=self.TextID)
            tc_text.addTask("AliasObjectAlphaTo", ObjectName="Sprite_BlackBar", To=0.0)
            tc_text.addTask("TaskEnable", ObjectName="Sprite_BlackBar")

            tc_text.addTask("AliasObjectAlphaTo", ObjectName="Sprite_BlackBar", Time=0.1 * 1000, To=1.0)  # speed fix
            tc_text.addTask("TaskEnable", ObjectName="Text_Message")

            tc_text.addTask("TaskDelay", Time=self.Time)

            tc_text.addTask("AliasObjectAlphaTo", ObjectName="Sprite_BlackBar", Time=0.1 * 1000, To=0.0)  # speed fix

            tc_text.addTask("TaskEnable", ObjectName="Text_Message", Value=False)
            tc_text.addTask("TaskEnable", ObjectName="Sprite_BlackBar", Value=False)

            if "Movie2" in self.Movie.getName():
                tc_movie.addTask("TaskMovie2Play", Movie2=self.Movie, Wait=True, Loop=False)
            else:
                tc_movie.addTask("TaskMoviePlay", Movie=self.Movie, Wait=True, Loop=False)

            tc_movie.addTask("TaskMovieLastFrame", Movie=self.Movie, Value=False)