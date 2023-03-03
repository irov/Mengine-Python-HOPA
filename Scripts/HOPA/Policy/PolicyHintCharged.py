from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintCharged(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintCharged, self)._onParams(params)
        self.Hint = DemonManager.getDemon("Hint")
        pass

    def _onGenerate(self, source):
        LayerGroup = GroupManager.getGroup("Hint")
        active = LayerGroup.getEnable()
        # print "PolicyHintCharged",active

        if active is False:
            return

        MovieGroup = self.Hint.getGroup()
        Movie_Charged = MovieGroup.getObject("Movie2_Charged")

        HintChargedSpeedFactor = 1

        Movie_Charged.setSpeedFactor(float(HintChargedSpeedFactor))

        source.addTask("TaskEnable", Object=Movie_Charged, Value=True)
        source.addTask("TaskMovie2Play", Movie2=Movie_Charged)
        source.addTask("TaskEnable", Object=Movie_Charged, Value=False)
        pass

    pass
