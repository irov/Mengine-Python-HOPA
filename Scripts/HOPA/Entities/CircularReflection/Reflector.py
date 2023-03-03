class Reflector(object):
    pass


class Reflexible(object):

    def __init__(self, node, pointer_left=None, pointer_right=None, point_forward=False):
        self.node = node
        self.pointer_left = pointer_left
        self.pointer_right = pointer_right
        self.point_forward = None
        pass

    def rearranged(self, pointer_left, pointer_right, point_forward):
        if self.pointer_right is not False:
            self.pointer_left = pointer_left
        if self.pointer_left is not False:
            self.pointer_right = pointer_right
        if self.point_forward is not False:
            self.point_forward = point_forward
        pass

    def __repr__(self):
        if self.pointer_left is None and self.pointer_right is None:
            return "%s" % self.node

        return "(L:%s,R:%s,F:%s)" % (self.pointer_left or 0, self.pointer_right or 0, self.point_forward or 0)
        pass


class Tape(object):

    def __init__(self, ReflexibleList):
        self.tape = ReflexibleList
        pass

    def __repr__(self):
        return repr(self.tape)
        pass

    def getTape(self):
        return self.tape
        pass

    def shift(self, direction, steps=1):
        if direction == 1:  # forward
            #            print self.tape[steps:],self.tape[:steps]
            self.tape = self.tape[steps:] + self.tape[:steps]
            pass
        else:  # torward
            #            print self.tape[-steps:],self.tape[:-steps]
            self.tape = self.tape[-steps:] + self.tape[:-steps]
            pass
        return self.tape
        pass

    def rearrangedTape(self, relativeList):
        for i, refl in enumerate(self.tape):
            left = relativeList[i - 1]
            next_index = (i + 1) % len(relativeList)  # n1
            forward = relativeList[i]
            right = relativeList[next_index]
            refl.rearranged(left, right, forward)
            pass
        pass


class TapeMachine(object):
    # aggregation
    def __init__(self, tapes):
        assert isinstance(tapes, list)
        self.tapes = tapes
        #        self.onInit()
        self.mapIt()
        pass

    def __repr__(self):
        return repr(self.tapes)
        pass

    #
    def mapIt(self):
        #        print type(self.tapes),self.tapes[0]
        for i, tape in enumerate(self.tapes[:-1]):
            relativeTape = self.tapes[i + 1]
            tape.rearrangedTape(relativeTape.getTape())
            pass
        pass

    def shift(self, tapeNum, direction, steps):
        tapeIndex = tapeNum - 1
        tape = self.tapes[tapeIndex]
        tape.shift(direction, steps)
        self.mapIt()
        #        if tapeNum < len(self.tapes) - 1:
        #            relativeTape = self.tapes[tapweIndex+1]
        #            tape.rearrangedTape(relativeTape.getTape())
        #            pass
        pass


class Connection(object):

    def __init__(self):
        pass

    pass

# if __name__ == "__main__":
#
#
#    rl1 = [Reflexible(i) for i in range(5)]
#    rl2 = [Reflexible(i) for i in range(5,10)]
#    tape1 = Tape(rl1)
#    tape2 = Tape(rl2)
##    print tape1
#    engine = TapeMachine([tape1,tape2])
#    for tape in engine.tapes:
#        print tape
#    engine.shift(2,-1,2)
#    for tape in engine.tapes:
#        print tape
##    tape.shift(1,3)
##    print tape.tape
##    tape.shift(1,10)
##    assert tape.tape == [0,1,2,3,4]
##    assert tape.tape == [2, 3, 4, 0, 1]
##    assert  tape.shift(-1,2) == [0,1,2,3,4]
