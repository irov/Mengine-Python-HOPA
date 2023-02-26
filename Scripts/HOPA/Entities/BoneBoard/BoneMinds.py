from Foundation.TaskManager import TaskManager

class BoneMinds(object):
    @staticmethod
    def play(mindId):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskMindPlay", MindID=mindId)
            pass