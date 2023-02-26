from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyAuthGoogleService(TaskAlias):

    def _onGenerate(self, source):
        SystemGoogleServices = SystemManager.getSystem("SystemGoogleServices")

        with source.addIfTask(SystemGoogleServices.isLoggedIn) as (true, false):
            true.addDummy()  # Already logged in :)
            false.addFunction(SystemGoogleServices.signIn)