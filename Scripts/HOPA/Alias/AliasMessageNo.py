from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasMessageNo(TaskAlias):
    def __init__(self):
        super(AliasMessageNo, self).__init__()

    def _onParams(self, params):
        super(AliasMessageNo, self)._onParams(params)

    def _onInitialize(self):
        super(AliasMessageNo, self)._onInitialize()

    def _onGenerate(self, source):
        if GroupManager.hasObject('Message', 'Movie2Button_No'):
            source.addTask('TaskMovie2ButtonClick', GroupName='Message', Movie2ButtonName='Movie2Button_No')


        elif GroupManager.hasObject('Message', 'MovieButton_No'):
            source.addTask('TaskMovieButtonClick', GroupName='Message', MovieButtonName='MovieButton_No')
        elif GroupManager.hasObject('Message', 'Button_No'):
            source.addTask('TaskButtonClick', GroupName='Message', ButtonName='Button_No')