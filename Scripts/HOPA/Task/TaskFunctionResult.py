from Foundation.Task.Task import Task


class TaskFunctionResult(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskFunctionResult, self)._onParams(params)

        self.Fn = params.get("Fn")
        self.Args = params.get("Args", ())
        pass

    def _onRun(self):
        res = self.Fn(*self.Args)

        return res
        pass

    pass
