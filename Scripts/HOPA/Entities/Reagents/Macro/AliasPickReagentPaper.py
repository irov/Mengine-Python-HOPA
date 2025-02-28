from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasPickReagentPaper(TaskAlias):
    def _onParams(self, params):
        super(AliasPickReagentPaper, self)._onParams(params)

        self.ItemObject = params.get("ItemObject")
        pass

    def _onGenerate(self, source):
        Demon = DemonManager.getDemon("ReagentsButton")
        movie = Demon.getObject("Movie_Paper")
        movieEntity = movie.getEntity()
        slot = movieEntity.getMovieSlot("paper")
        positionTo = slot.getWorldPosition()
        itemEntity = self.ItemObject.getEntity()

        time = 2.0
        time *= 1000  # speed fix

        source.addTask("TaskNodeBezier2To", Node=itemEntity, To=positionTo, Time=time)
        source.addDisable(self.ItemObject)
        source.addParam(Demon, "EnablePaper", True)
        pass

    pass
