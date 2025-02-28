from Foundation.TaskManager import TaskManager

from Target import Target


class ChasingSystem(object):
    queue = []  # fifo
    current = None

    @staticmethod
    def load(movie_objects_list, movieCarrier, enigmaObject):
        for movie in movie_objects_list:
            target = Target(movie, movieCarrier, enigmaObject)
            ChasingSystem.queue.append(target)
            pass
        pass

    @staticmethod
    def run_chase():
        with TaskManager.createTaskChain(Name="Chasing") as tc:
            for i, target in enumerate(ChasingSystem.queue):
                tc.addFunction(ChasingSystem.__update_current, target)
                tc.addFunction(target.chase)
                tc.addListener(Notificator.onChase, Filter=ChasingSystem.get_passed)
                tc.addPrint("ChaseComplete:%d" % (i,))
                pass
            pass
        pass

    @staticmethod
    def __update_current(tg):
        ChasingSystem.current = tg
        pass

    @staticmethod
    def stop_chase():
        if TaskManager.existTaskChain("Chasing"):
            TaskManager.cancelTaskChain("Chasing")
        ChasingSystem.current = None
        for exist_target in ChasingSystem.queue:
            exist_target.cleanUpMovie(True)
        ChasingSystem.queue[:] = []
        ChasingSystem.current = None
        pass

    @staticmethod
    def get_passed(targetInstance):
        if targetInstance not in ChasingSystem.queue:
            return False
        pass

        if targetInstance == ChasingSystem.queue[0]:
            ChasingSystem.queue.pop(0)
            return True
            pass
        pass  # return targetInstance.get_passed()
