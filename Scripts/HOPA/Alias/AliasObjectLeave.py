from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias

class AliasObjectLeave(MixinObject, TaskAlias):
    def _onParams(self, params):
        super(AliasObjectLeave, self)._onParams(params)
        self.AutoEnable = params.get("AutoEnable", True)
        self.isMouseEnter = params.get("isMouseEnter", False)

    def _onGenerate(self, source):
        ObjectType = self.Object.getType()

        if ObjectType == "ObjectSocket":
            source.addTask("TaskSocketLeave", Socket=self.Object, AutoEnable=self.AutoEnable, isMouseEnter=self.isMouseEnter)

        elif ObjectType == "ObjectButton":
            source.addTask("TaskButtonLeave", Button=self.Object, isMouseEnter=self.isMouseEnter)

        elif ObjectType == "ObjectMovieButton":
            source.addTask("TaskMovieButtonLeave", MovieButton=self.Object)

        elif ObjectType == "ObjectTransition":
            source.addTask("TaskTransitionLeave", Transition=self.Object)

        elif ObjectType == "ObjectMovie2":
            # macro race case fix
            if self.AutoEnable is False and self.Object.getEnable() is False:
                source.addBlock()
                return
            source.addTask("TaskMovie2SocketLeave", Movie2=self.Object, Any=True, AutoEnable=self.AutoEnable)