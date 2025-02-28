from Foundation.TaskManager import TaskManager

from BoneMinds import BoneMinds


class BoneItem(object):
    def __init__(self, prev, item, movie_use, movie_wrong, movie_add, movie_over):
        self.item = item
        self.prev = prev
        self.movie_use = movie_use
        self.movie_wrong = movie_wrong
        self.movie_add = movie_add
        self.movie_over = movie_over
        self.active = False
        self.useful = False
        self.after_create()
        pass

    def getActive(self):
        return self.active
        pass

    def restore_active(self):
        if self.prev is not None:
            self.prev.setEnable(False)

        self.item.setEnable(True)
        self.item.setInteractive(True)
        self.active = True
        pass

    def set_active(self):
        self.restore_active()
        # BoneMinds.play("ID_MIND_ADDBONE")
        self.place(self.movie_add)
        self.play(self.movie_add)
        pass

    def make_useful(self):
        self.useful = True
        pass

    def after_create(self):
        if self.prev is not None:
            self.prev.setEnable(True)
            self.prev.setInteractive(True)
            self.item.setEnable(False)
        else:
            self.set_active()
            pass

        self.movie_use.setEnable(False)
        self.movie_wrong.setEnable(False)
        self.movie_add.setEnable(False)
        self.movie_over.setEnable(False)
        pass

    def make_action(self, notify_arg=None, wrong=False):
        if not self.active:
            return

        if self.useful and not wrong:
            BoneMinds.play("ID_MIND_USEBONE")
            self.place(self.movie_use)
            self.play(self.movie_use, notify_arg)
            self.useful = False
            pass
        elif not self.useful or wrong:
            self.playWrong()
        pass

    def place(self, obj):
        obj.setEnable(True)
        pass

    def play(self, obj, note=None):
        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskMoviePlay", Movie=obj)
            tc.addDisable(obj)
            if note:
                tc.addNotify(Notificator.onBoneUse, note)
            pass
        pass

    def playWrong(self):
        # wrap for system Wrong Bones
        BoneMinds.play("ID_MIND_WHRONGBONE")
        self.place(self.movie_wrong)
        self.play(self.movie_wrong)
        return True
        pass

    def getOver(self):
        return self.movie_over
