class Hand(object):
    Slot = "Item"
    CarrierSlot = "Carrier"

    def __init__(self, movieCarriersTuple, moviesV, partitions, termMovie):
        self.HM = Hand.HorizontalMovable(*movieCarriersTuple)
        self.VM = Hand.VerticalMovable(*moviesV)
        self.terminate = False
        self.partitions = partitions
        self.terminationMovie = termMovie
        self.onInitialize()
        pass

    class HorizontalMovable(object):

        def __init__(self, moviesRight, moviesLeft):
            self.carry_node = None
            self.homeless = []
            self.right = moviesRight
            self.left = moviesLeft
            self.internal_state = 0
            self._updateNode()
            pass

        def onDeactivate(self):
            self.destroy()
            pass

        def onReset(self):
            self.internal_state = 0
            self._updateNode()

        def getCursor(self):
            return self.internal_state
            pass

        def _updateNode(self):
            movie = self.right[self.internal_state]
            en = movie.getEntity()
            carrierNode = en.getMovieSlot(Hand.CarrierSlot)
            self.carry_node = carrierNode
            pass

        def leftMove(self):
            if self.internal_state == 0:
                return
                pass

            self.internal_state -= 1
            leftMovie = self.left[self.internal_state]

            leftEn = leftMovie.getEntity()
            carrierNode = leftEn.getMovieSlot(Hand.CarrierSlot)
            self.carry_node = carrierNode
            return leftMovie
            pass

        def rightMove(self):
            #            print "i ", self.internal_state, len(self.left)
            limit = len(self.left) - 1
            if self.internal_state > limit:
                return
                pass
            rightMovie = self.right[self.internal_state]
            self.internal_state += 1 if self.internal_state <= limit else 0
            rightEn = rightMovie.getEntity()
            carrierNode = rightEn.getMovieSlot(Hand.CarrierSlot)
            self.carry_node = carrierNode
            return rightMovie
            pass

        def addChild(self, Object):
            En = Object.getEntity()
            self.carry_node.addChild(En)
            Object.setPosition((0, 0))
            self.addToHomeless(En)
            pass

        def addToHomeless(self, en):
            if en not in self.homeless:
                self.homeless.append(en)
                pass
            pass

        def cleanHomeless(self):
            for en in self.homeless:
                en.removeFromParent()
                pass
            self.homeless = []
            pass

        def destroy(self):
            self.cleanHomeless()
            self.carry_node = None
            pass

    class VerticalMovable(object):

        def __init__(self, movieTopUp, movieTopDown, movieBotUp, movieBotDown, movieFinalUp, movieFinalDown):
            self.movieTopUp = movieTopUp
            self.movieTopDown = movieTopDown
            self.movieBotUp = movieBotUp
            self.movieBotDown = movieBotDown
            self.movieFinalUp = movieFinalUp
            self.movieFinalDown = movieFinalDown
            self.carry_slot = None
            self.upstate = True
            self.slotConst = Hand.Slot
            self.homeless = []
            self.monkey = None
            self.partition = None
            self.curr_movie = self.movieBotDown
            self.movieBotDown.setEnable(True)
            self.movieBotUp.setEnable(False)
            self.movieTopUp.setEnable(False)
            self.movieFinalDown.setEnable(False)
            self.movieFinalUp.setEnable(False)
            self.movieTopDown.setEnable(False)
            self.slugCbQueue = []

            self.partition = None
            pass

        def onDeactivate(self):
            if self.monkey is not None:
                self.monkey.removeFromParent()
            pass

        def hasMonkey(self):
            return self.monkey is not None
            pass

        def onReset(self):
            self.curr_movie = self.movieBotDown
            self.movieBotUp.setEnable(False)
            self.movieTopUp.setEnable(False)
            self.movieTopDown.setEnable(False)

        def isup(self):
            """
            cant move left or right if state is down
            """
            return self.upstate
            pass

        def getAndDumpSlug(self):
            dump = self.slugCbQueue
            self.slugCbQueue = []
            return dump
            pass

        def calls(self, bound_method):
            """
            print current run method
            """

            def show(self, *args):
                return bound_method(self, *args)

            return show
            pass

        def addChild(self):
            if self.monkey is None:
                #                print "none monkey"
                return
                pass
            En = self.monkey
            Object = En.getObject()
            self.carry_slot.addChild(En)
            Object.setPosition((0, 0))
            self.addToHomeless(En)
            pass

        def addToHomeless(self, en):
            if en not in self.homeless:
                self.homeless.append(en)
                pass
            pass

        def partitionExec(self):
            if self.partition is None:
                return
                pass

            if self.monkey is None:
                self.monkey = self.partition.take()
                return
                pass
            else:
                self.partition.give(self.monkey)
                self.monkey = None
                pass
            pass

        def updateNode(self, objectMovie):
            en = objectMovie.getEntity()
            objectMovie.setEnable(True)
            node = en.getMovieSlot(self.slotConst)
            self.carry_slot = node
            self.addChild()
            if objectMovie is not self.curr_movie:  # disable if not same movie
                self.curr_movie.setEnable(False)
                pass
            pass

        def getDown(self, partitionInst):
            self.upstate = False
            pState = partitionInst.getState()

            if partitionInst.isEmpty() is True:
                movie = self.movieBotDown

                if partitionInst.isFinal() is True:
                    movie = self.movieFinalDown
                    pass

                self.partition = partitionInst
                self.slugCbQueue.append(self.partitionExec)
                self.updateNode(movie)
                self.slugCbQueue.append(self.addChild)
                self.curr_movie = movie
                return movie
                pass

            elif pState == 0:
                #               if we alredy get monkey in hand we must move to top otherwise
                #               moves to bot and catch monkey
                self.partition = partitionInst

                if partitionInst.isFinal() is True:
                    movie = self.movieFinalDown
                    pass

                elif self.monkey is not None:
                    movie = self.movieTopDown
                    pass

                else:
                    movie = self.movieBotDown
                    pass
                self.slugCbQueue.append(self.partitionExec)
                self.updateNode(movie)
                self.slugCbQueue.append(self.addChild)
                self.curr_movie = movie
                return movie
                pass

            elif pState == 1 or pState == 2:
                self.partition = partitionInst
                movie = self.movieTopDown

                if partitionInst.isFinal() is True:
                    movie = self.movieFinalDown
                    pass

                self.slugCbQueue.append(self.partitionExec)
                self.updateNode(movie)
                self.slugCbQueue.append(self.addChild)
                self.curr_movie = movie
                return movie
                pass
            pass

        def getUp(self, partitionInst):
            self.upstate = True
            pState = partitionInst.getState()
            if partitionInst.isEmpty() is True:
                movie = self.movieBotUp
                if partitionInst.isFinal() is True:
                    movie = self.movieFinalUp

                self.updateNode(movie)
                self.addChild()
                self.curr_movie = movie
                return movie
                pass

            elif pState == 0:
                #                if we already get down and taked monkey partion state becomes 0 but
                #                current view position is top so need to check of monkey state

                if partitionInst.isFinal() is True:
                    movie = self.movieFinalUp
                    pass

                elif self.monkey is None:
                    movie = self.movieBotUp
                    pass

                else:
                    movie = self.movieTopUp
                    pass
                self.updateNode(movie)
                self.addChild()
                self.curr_movie = movie
                return movie
                pass

            elif pState == 1 or pState == 2:
                movie = self.movieTopUp
                if partitionInst.isFinal() is True:
                    movie = self.movieFinalUp
                    pass

                self.updateNode(movie)
                self.addChild()
                self.curr_movie = movie
                return movie
                pass
            pass

        pass

    def onInitialize(self):
        self.HM.addChild(self.VM.curr_movie)
        pass

    def onDeactivate(self):
        self.VM.onDeactivate()
        self.HM.onDeactivate()
        pass

    def onReset(self):
        self.VM.onReset()
        self.HM.onReset()
        self.onInitialize()
        pass

    def flushTerm(self):
        self.terminate = False
        pass

    def calls(self, bound_method):
        """
        print current run method
        """

        def show(self, *args):
            return bound_method(self, *args)

        return show
        pass

    def term(self, bound_method):
        def wrap(self, *args):
            if self.terminate is True:
                return
            else:
                return bound_method(self, *args)

        return wrap

    @term
    def moveLeft(self, scope):
        upstate = self.VM.isup()
        if upstate is False:
            self.terminate = True
            return
            pass

        mov = self.HM.leftMove()
        if mov is None:
            self.terminate = True
            return
            pass

        vertical = self.VM.curr_movie
        self.HM.addChild(vertical)
        scope.addTask("TaskMoviePlay", Movie=mov)
        pass

    @term
    def moveRight(self, scope):
        upstate = self.VM.isup()
        if upstate is False:
            self.terminate = True
            return
            pass

        mov = self.HM.rightMove()
        if mov is None:
            self.terminate = True
            return
            pass
        vertical = self.VM.curr_movie
        self.HM.addChild(vertical)
        scope.addTask("TaskMoviePlay", Movie=mov)
        pass

    @term
    def moveUp(self, scope):
        upstate = self.VM.isup()
        if upstate is True:
            self.terminate = True
            return
            pass

        state = self.HM.getCursor()
        partitionInst = self.partitions[state]
        mov = self.VM.getUp(partitionInst)
        self.HM.addChild(mov)
        scope.addTask("TaskMoviePlay", Movie=mov)
        pass

    @term
    def moveDown(self, scope):
        upstate = self.VM.isup()
        if upstate is False:
            self.terminate = True
            return
            pass

        state = self.HM.getCursor()
        #        print " Current partition is ", state
        partitionInst = self.partitions[state]
        if partitionInst.isFull() is True and self.VM.hasMonkey() is True:
            self.terminate = True
            return
            pass

        if partitionInst.lastHold is True and self.VM.hasMonkey() is False:
            self.terminate = True
            return
            pass

        mov = self.VM.getDown(partitionInst)
        self.HM.addChild(mov)
        methodsQueue = self.VM.getAndDumpSlug()
        scope.addTask("TaskMoviePlay", Movie=mov)
        for method in methodsQueue:
            scope.addFunction(method)
            pass

        if partitionInst.isFinal() is True:
            scope.addScope(self.moveUp)
            pass
        pass

    def moveBack(self, scope):
        # tricky
        if self.terminate is False:
            return
            pass

        self.terminate = False
        state = self.HM.getCursor()
        upstate = self.VM.isup()

        scope.addEnable(self.terminationMovie)
        scope.addTask("TaskMoviePlay", Movie=self.terminationMovie)
        scope.addDisable(self.terminationMovie)

        if upstate is False:
            scope.addScope(self.moveUp)
            pass

        for step in range(state):
            scope.addScope(self.moveLeft)
            pass
        pass
