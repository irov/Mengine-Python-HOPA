from Foundation.DatabaseManager import DatabaseManager

class MetalDetectorManager(object):
    detectors = {}

    class SingleDetector(object):
        def __init__(self, InventoryItemName, InteractRadius, Range):
            self.InventoryItemName = InventoryItemName
            self.InteractRadius = InteractRadius
            self.Range = Range
            pass

        def getRadius(self):
            return self.InteractRadius
            pass

        def getItem(self):
            return self.InventoryItemName

        def getRange(self):
            return self.Range

    @staticmethod
    def onFinalize():
        MetalDetectorManager.detectors = {}
    pass

    @staticmethod
    def loadItems(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            DemonName = record.get("Name")
            Item = record.get("Item")
            Radius = record.get("InteractRadius")
            Rage = record.get("Range")
            MetalDetectorManager.addRow(DemonName, Item, Radius, Rage)
            pass
        pass

    @staticmethod
    def addRow(DemonName, Item, Radius, Rage):
        data = MetalDetectorManager.SingleDetector(Item, Radius, Rage)
        MetalDetectorManager.detectors[DemonName] = data
        pass

    @staticmethod
    def hasDetector(DemonName):
        return DemonName in MetalDetectorManager.detectors
        pass

    @staticmethod
    def getDetector(DemonName):
        if not MetalDetectorManager.hasDetector(DemonName):
            Trace.log("MetalDetectorManager.hasDetector: not found item %s " % (DemonName), 0, '')
            return False

        return MetalDetectorManager.detectors[DemonName]

    @staticmethod
    def getItemName(DemonName):
        detector = MetalDetectorManager.getDetector(DemonName)
        return detector.getItem()

    @staticmethod
    def getRadius(DemonName):
        detector = MetalDetectorManager.getDetector(DemonName)
        return detector.getRadius()

    @staticmethod
    def getRange(DemonName):
        detector = MetalDetectorManager.getDetector(DemonName)
        return detector.getRange()