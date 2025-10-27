from Foundation.TaskManager import TaskManager
from HOPA.Entities.InventoryBase import InventoryBase
from HOPA.HOGManager import HOGManager

InventoryBase = Mengine.importEntity("InventoryBase")

class HOGInventorySlot(object):
    def __init__(self, textID):
        self.textID = textID
        self.field = None
        self.count = None
        self.point = None
        self.found = False
        pass

    def getTextID(self):
        return textID
        pass

    def setPoint(self, value):
        self.point = value
        pass

    def getPoint(self):
        return self.point
        pass

    def incref(self):
        if self.count is None:
            self.count = 2
        else:
            self.count += 1
            pass
        pass

    def decref(self):
        if self.count is None:
            self.found = True
            return

        self.count -= 1

        if self.count == 0:
            self.found = True
            pass
        pass

    def isMulty(self):
        return self.count is not None
        pass

    def isFound(self):
        return self.found
        pass

    def setTextField(self, field):
        self.field = field
        pass

    def getTextField(self):
        return self.field
        pass

    def getCount(self):
        return self.count
        pass

    def updateText(self):
        self.field.setTextID(self.textID)

        if self.isMulty() is True and self.count > 0:
            self.field.setTextFormatArgs(self.count)
            pass
        pass

    def release(self):
        if self.field is not None:
            Mengine.destroyNode(self.field)
            self.field = None


class HOGInventory(InventoryBase):
    HOG_TEXT_COLOR_OFF = (0.3, 0.3, 0.3, 1)

    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)

        Type.addAction("MaxItemTextWrap", Update=HOGInventory._restoreMaxItemTextWrap)

        Type.addAction("Wrap")
        Type.addAction("MaxColumn")
        Type.addAction("MaxRow")

        Type.addAction("HOGName")
        Type.addActionActivate("HOGItems", Update=HOGInventory._updateHOGItems)

        Type.addAction("FoundItems", Append=HOGInventory._appendFoundItems)
        pass

    def __init__(self):
        super(HOGInventory, self).__init__()

        self.slots = {}

        self.rows = []
        self.itemTextSpace = 0.0
        self.itemTextWidth = 0.0
        pass

    def _onInitialize(self, obj):
        super(HOGInventory, self)._onInitialize(obj)
        pass

    def getSlots(self):
        return self.slots
        pass

    def getSlotByName(self, name):
        textID = HOGManager.getHOGItemTextID(self.HOGName, name)

        if textID not in self.slots.keys():
            return None

        return self.slots[textID]
        pass

    def _calculateDimentions(self, count):
        column = int(pow(count, 0.5))
        if column == 0:
            return
            pass
        row = int(count / column)
        extra = count - column * row
        enum = 0

        self.rows = []
        for i in range(column):
            extra_add = min(extra, 1)
            if extra > 0:
                extra -= 1
                pass

            row_range = range(enum, enum + row + extra_add)
            self.rows.append(row_range)
            enum += row + extra_add
            pass

        width = float(self.Wrap[1][0] - self.Wrap[0][0])
        self.itemTextSpace = (width - self.itemTextWidth * self.MaxRow) / float(self.MaxRow - 1)
        pass

    def _getColumnRowFromIndex(self, index):
        for column, row in enumerate(self.rows):
            if index in row:
                return column, row.index(index)
                pass
            pass

        return None
        pass

    def _restoreMaxItemTextWrap(self, wrap):
        self.itemTextWidth = wrap[1][0] - wrap[0][0]
        pass

    def _updateHOGItems(self, value):
        if value is None:
            return
            pass

        self.slots = {}

        for name in self.HOGItems:
            textID = HOGManager.getHOGItemTextID(self.HOGName, name)

            if textID not in self.slots:
                self.slots[textID] = HOGInventorySlot(textID)
                pass
            else:
                slot = self.slots[textID]
                slot.incref()
                pass
            pass

        for name in self.FoundItems:
            textID = HOGManager.getHOGItemTextID(self.HOGName, name)
            if textID in self.slots:
                slot = self.slots[textID]
                slot.decref()
                pass
            pass

        count = len(self.slots)

        if self.MaxColumn * self.MaxRow < count:
            Trace.log("HOGInventory", 0, "HOGInventory %s FindItems %s > max count %s" % (
                self.object.name, self.HOGItems, self.MaxColumn * self.MaxRow))
            return

        self._calculateDimentions(count)

        for index, value in enumerate(self.slots.items()):
            column, row = self._getColumnRowFromIndex(index)
            textID, slot = value

            textField = self._createTextField(textID, column, row)

            slot.setTextField(textField)
            slot.updateText()
            self._updateTextFieldPos(textField, column, row, slot)

        with TaskManager.createTaskChain(Name="HOGInventory", Group=self.object) as tc:
            itemCount = len(self.FoundItems)
            with tc.addParallelTask(itemCount) as tcho:
                for tchog, foundItemName in zip(tcho, self.FoundItems):
                    tchog.addTask("TaskHOGInventoryCrossOut", HOGItemName=foundItemName, Immediately=True)

    def _onDeactivate(self):
        if TaskManager.existTaskChain("HOGInventory") is True:
            TaskManager.cancelTaskChain("HOGInventory")
            pass

        for slot in self.slots.itervalues():
            slot.release()
            pass

        self.slots = {}

        self.rows = []
        pass

    def _calculatePos(self, textField, column, row):
        width = float(self.Wrap[1][0] - self.Wrap[0][0])
        height = float(self.Wrap[1][1] - self.Wrap[0][1])

        row_count = len(self.rows[column])

        deltha = width / float(row_count * 2)

        posx = self.Wrap[0][0] + ((row * 2) + 1) * deltha

        column_count = len(self.rows)
        column_height = height / float(min(column_count + 1, self.MaxColumn))
        posy = self.Wrap[0][1] + height * 0.5 - (column_height * column_count) * 0.5 + column_height * column

        text_length = textField.getTextSize()

        tposy = posy + column_height * 0.5 - text_length.y * 0.5

        scale = 1.0

        value = (posx, tposy, scale)

        return value
        pass

    def _createTextField(self, textID, column, row):
        textField = Mengine.createNode("TextField")
        textField.setCenterAlign()

        self.addChild(textField)

        return textField
        pass

    def _updateTextFieldPos(self, textField, column, row, slot):
        posx, posy, scale = self._calculatePos(textField, column, row)

        textField.setScale((scale, scale, 1.0))
        textField.setLocalPosition((posx, posy))
        slot.setPoint((posx, posy))
        pass

    def _appendFoundItems(self, id, value):
        slot = self.getSlotByName(value)
        if slot is None:
            return
            pass
        slot.decref()
        slot.updateText()

        if slot.isFound() is True:
            Notification.notify(Notificator.onHOGInventoryFoundItem, value, True)
        else:
            Notification.notify(Notificator.onHOGInventoryFoundItem, value, False)
