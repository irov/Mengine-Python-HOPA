from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasMessageYes(TaskAlias):
    def __init__(self):
        super(AliasMessageYes, self).__init__()

    def _onParams(self, params):
        super(AliasMessageYes, self)._onParams(params)

    def _onInitialize(self):
        super(AliasMessageYes, self)._onInitialize()

    def _onGenerate(self, source):
        if GroupManager.hasObject('Message', 'Movie2Button_Yes'):
            source.addTask('TaskMovie2ButtonClick', GroupName='Message', Movie2ButtonName='Movie2Button_Yes')

        elif GroupManager.hasObject('Message', 'MovieButton_Yes'):
            source.addTask('TaskMovieButtonClick', GroupName='Message', MovieButtonName='MovieButton_Yes')
        elif GroupManager.hasObject('Message', 'Button_Yes'):
            source.addTask('TaskButtonClick', GroupName='Message', ButtonName='Button_Yes')
