from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias


class AliasObjectEnter(MixinObject, TaskAlias):
    def _onParams(self, params):
        super(AliasObjectEnter, self)._onParams(params)
        self.AutoEnable = params.get("AutoEnable", True)

    def _onGenerate(self, source):
        ObjectType = self.Object.getType()

        if ObjectType == "ObjectSocket":
            source.addTask("TaskSocketEnter", Socket=self.Object, AutoEnable=self.AutoEnable)

        elif ObjectType == "ObjectButton":
            source.addTask("TaskButtonEnter", Button=self.Object)

        elif ObjectType == "ObjectMovieButton":
            source.addTask("TaskMovieButtonEnter", MovieButton=self.Object)

        elif ObjectType == "ObjectTransition":
            source.addTask("TaskTransitionEnter", Transition=self.Object)

        elif ObjectType == "ObjectMovie2":
            # macro race case fix
            if self.AutoEnable is False and self.Object.getEnable() is False:
                source.addBlock()
                return
            source.addTask("TaskMovie2SocketEnter", Movie2=self.Object, Any=True, AutoEnable=self.AutoEnable)
