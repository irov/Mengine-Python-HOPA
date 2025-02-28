from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from Notification import Notification


class InstructionPullOut(BaseEntity):

    def __init__(self):
        super(InstructionPullOut, self).__init__()
        self.ParentLayer = "Puzzle"
        self.block = False
        self.state = False
        self.clean_up = []
        pass

    def _onActivate(self):
        self.attachPreparation()

        self.Layer = SceneManager.getLayerScene(self.ParentLayer)
        self.PullInn = Notification.addObserver(Notificator.onInstructionPullIn, self.directPlay)
        self.Exit = Notification.addObserver(Notificator.onFinalize, self._forceClean)
        pass

    def _forceClean(self, *params):
        self._onDeactivate()
        return True
        pass

    def _onDeactivate(self):
        for trash in self.clean_up:
            trash.removeFromParent()
        self.clean_up = []
        Notification.removeObserver(self.PullInn)
        Notification.removeObserver(self.Exit)
        pass

    def attachPreparation(self):
        self.group = self.object.getGroup()
        self.MoviePull = self.object.getObject("Movie_PullOut")
        movieEn = self.MoviePull.getEntity()

        self.slotNode = movieEn.getMovieSlot("Back")
        sprite = self.group.getObject("Sprite_BackGround")
        spriteEn = sprite.getEntity()
        self.slotNode.addChild(spriteEn)
        sprite.setPosition((0, 0))
        self.clean_up.append(spriteEn)

        slotNode = movieEn.getMovieSlot("Text")
        text = self.group.getObject("Text_Minigame1")
        textEn = text.getEntity()
        slotNode.addChild(textEn)
        text.setPosition((0, 0))
        self.clean_up.append(textEn)

    def directPlay(self, instruction, directPlay):
        if instruction is not self.group:
            return False

        instructionEn = instruction.getEntity()
        is_add = instructionEn.getParent() is not self.Layer
        if is_add:
            self.Layer.addChild(instructionEn)

        if self.block:
            return False

        if self.state == directPlay:
            return False
        #            directPlay = not self.state
        #            self.state = directPlay
        else:
            self.state = directPlay

        with TaskManager.createTaskChain() as tc:
            tc.addFunction(self.setBlock, True)
            tc.addTask("TaskMoviePlay", Movie=self.MoviePull, Wait=True, Reverse=not directPlay)
            if is_add:
                tc.addFunction(self.Layer.removeChild, instructionEn)

            tc.addFunction(self.setBlock, False)
        return False

    def setBlock(self, block):
        self.block = block
        pass
