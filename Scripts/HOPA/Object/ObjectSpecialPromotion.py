from Foundation.Object.DemonObject import DemonObject
from Foundation.TaskManager import TaskManager
from HOPA.Entities.SpecialPromotion.SpecialPromotion import EVENT_WINDOW_CLOSE, EVENT_GET_PURCHASED


class ObjectSpecialPromotion(DemonObject):
    EVENT_WINDOW_CLOSE = EVENT_WINDOW_CLOSE
    EVENT_GET_PURCHASED = EVENT_GET_PURCHASED

    show_queue = []

    def _addToShowQueue(self, special_prod_id):
        if special_prod_id in self.show_queue:
            return
        self.show_queue.append(special_prod_id)

    def _waitMoment(self):
        if len(self.show_queue) == 0:
            return

        if TaskManager.existTaskChain("SpecialPromotionWaitMoment") is True:
            return

        def _cb(isSkip):
            if self.isActive() is False:
                self._waitMoment()

        with TaskManager.createTaskChain(Name="SpecialPromotionWaitMoment", Cb=_cb) as tc:
            tc.addListener(Notificator.onSceneActivate)

            with tc.addIfTask(self.isActive) as (tc_true, tc_false):
                def _reverseQueue():
                    # we do reverse for take first queued item, not last
                    self.show_queue = self.show_queue[::-1]

                tc_true.addFunction(_reverseQueue)

                with tc_true.addForTask(len(self.show_queue)) as (it, tc_for):
                    def _scope(source):
                        special_prod_id = self.show_queue.pop()
                        with source.addParallelTask(2) as (cancel, run):
                            with cancel.addRaceTask(2) as (purchased, closed):
                                purchased.addEvent(EVENT_GET_PURCHASED)
                                closed.addEvent(EVENT_WINDOW_CLOSE)
                            run.addFunction(self.run, special_prod_id)

                    tc_for.addScope(_scope)

    def run(self, special_prod_id):
        if self.isActive():
            self.entity.run(special_prod_id)
            return
        if _DEVELOPMENT is True:
            Trace.msg_err("SpecialPromotion is not active for run({}), add to queue = {}".format(special_prod_id, self.show_queue))

        self._addToShowQueue(special_prod_id)
        self._waitMoment()
