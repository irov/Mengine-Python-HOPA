class Field(object):
    def __init__(self, border, data):
        self.metric = data.getMetric()
        self.fieldData = data.getData()
        self.border = border  # polygon
        self.part_dimension = ()
        self.noLinear = []
        self.MaskPattern = []
        self._onInitialize()
        self.fieldCursor = (0, 0)
        self.track = 0
        self.escaped = False
        self._start = None
        pass

    def _onInitialize(self):
        self._noLinearGrid()
        self.niceStamp()
        assert len(self.border) == 2
        pass

    def initFieldCursor(self):
        for rowNum, values in self.fieldData.iteritems():
            for i, value in enumerate(values):
                if value == 3:
                    self.fieldCursor = rowNum, i
                    pass
                pass
            pass
        pass

    def returnToStart(self):
        self.initFieldCursor()
        smooth_position = self.getFieldCursor()
        return smooth_position
        pass

    def isFallDown(self):
        xMove, yMove = self.fieldCursor
        xBound, yBound = self.metric
        if xMove == 0 or xMove == xBound - 1:
            return True
            pass
        elif yMove == 0 or yMove == yBound - 1:
            return True
            pass
        else:
            return False
            pass
        pass

    def getFieldCursor(self):
        cord2 = self.indexToCord(self.fieldCursor)
        return cord2
        pass

    def _noLinearGrid(self):
        vertical_parts = self.metric[0] - 1
        horizontal_parts = self.metric[1] - 1
        _height = self._width()
        _width = self._height()
        _partHeight = _height / horizontal_parts
        _partWidth = _width / vertical_parts
        self.part_dimension = (_partWidth, _partHeight)
        assert int(_partHeight) == int(_partWidth), (vertical_parts, horizontal_parts)
        apexes = self.border
        apex = apexes[0]
        for row in range(vertical_parts + 1):
            column = []
            for col in range(horizontal_parts + 1):
                _y = apex[1] + row * _partHeight
                _x = apex[0] + col * _partHeight
                mTuple = (_x, _y)
                column.append(mTuple)
                pass
            self.noLinear.append(column)
            pass
        return self.noLinear
        pass

    def isEscaped(self):
        return self.escaped
        pass

    def indexToCord(self, indexes):
        i, j = indexes
        cord2 = self.noLinear[i][j]
        return cord2
        pass

    def setEscaping(self):
        for rowNum, values in self.fieldData.iteritems():
            for i, value in enumerate(values):
                if value == 2:
                    self.MaskPattern[rowNum][i] = None
                    pass
                pass
            pass
        pass

    def defineMove(self, direction):
        fromPoint = self.fieldCursor
        # None or cordPoint, switch direction 1-2-3-4
        #        currentIndexes = self.cordToIndex(fromPoint)
        row, column = fromPoint

        if direction == 1:  # right
            _rowList = self.MaskPattern[row][column:]

            if False in _rowList:
                index = _rowList.index(False) + column - 1
                pass
            else:
                index = self.metric[1] - 1
                pass

            escapeLs = _rowList[:index]

            if None in escapeLs:
                index = escapeLs.index(None)
                self.escaped = True
                pass

            self.fieldCursor = (row, index)
            self.track = index - column
            return self.fieldCursor
            pass

        elif direction == 2:  # down
            transform = zip(*self.MaskPattern)
            _rowList = transform[column][row + 1:]
            f_index = 0

            if False in _rowList:
                f_index = _rowList.index(False)
                index = f_index + row
                pass
            else:
                f_index = self.metric[0] - 1
                index = self.metric[0] - 1
                pass

            escapeLs = _rowList[:f_index]

            if None in escapeLs:
                index = escapeLs.index(None) + row
                self.escaped = True
                pass

            self.track = index - row
            self.fieldCursor = (index, column)
            return self.fieldCursor
            pass

        elif direction == 3:  # left
            _rowList = self.MaskPattern[row][:column]
            if False in _rowList:
                rev = list(reversed(_rowList))
                #                index = _rowList.index(False)+1
                index = column - rev.index(False)
                pass
            else:
                index = 0
                pass

            escapeLs = _rowList[:index]

            if None in escapeLs:
                index = escapeLs.index(None)
                self.escaped = True
                pass

            self.track = column - index
            self.fieldCursor = (row, index)
            return self.fieldCursor

        elif direction == 4:  # up
            transform = zip(*self.MaskPattern)
            _rowList = transform[column][:row]

            rever = list(reversed(_rowList))
            f_index = 0

            if False in _rowList:
                f_index = rever.index(False)
                index = row - f_index  # 11111
                pass
            else:
                index = 0
                pass

            escapeLs = rever[:f_index]

            if None in escapeLs:
                index = row - escapeLs.index(None)
                self.escaped = True
                pass

            self.track = row - index
            self.fieldCursor = (index, column)
            return self.fieldCursor
            pass
        pass

    def niceStamp(self, stamp=None):
        # None - escape state, True - allow state, False - 	forbidden state
        # rerpFlag = "____"
        self.MaskPattern = [["%s_%s" % (j, i) for i in range(self.metric[1])] for j in range(self.metric[0])]
        for rowNum, values in self.fieldData.iteritems():
            for i, value in enumerate(values):
                if value == 1:
                    self.MaskPattern[rowNum][i] = False
                    pass
                pass
            pass
        return
        pass

    def getInternBoundaries(self):
        # for only tests
        boundCords = []
        newMask = zip(*self.MaskPattern)
        newMask = self.MaskPattern
        for i in range(len(self.noLinear)):
            for j in range(len(self.noLinear[0])):
                if newMask[i][j] is False:
                    boundCords.append(self.noLinear[i][j])
                    pass
                pass
            pass
        return boundCords
        pass

    def _width(self):
        #        sorted_w = sorted(self.border, key=lambda x: x[0])
        _head = self.border[0]
        _tail = self.border[-1]
        width = _tail[0] - _head[0]
        assert width > 0
        return width

    def _height(self):
        #        sorted_h = sorted(self.border, key=lambda x: x[1])
        _head = self.border[0]
        _tail = self.border[-1]
        height = _tail[1] - _head[1]
        assert height > 0
        return height
        pass
