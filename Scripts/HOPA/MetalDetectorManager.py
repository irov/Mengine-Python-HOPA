from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class MetalDetectorManager(Manager):
    detectors = {}

    class SingleDetector(object):
        def __init__(self, InventoryItemName, InteractRadius, Range):
            self.InventoryItemName = InventoryItemName
            self.InteractRadius = InteractRadius
            self.Range = Range

        def getRadius(self):
            return self.InteractRadius

        def getItem(self):
            return self.InventoryItemName

        def getRange(self):
            return self.Range

    @staticmethod
    def _onFinalize():
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

    @staticmethod
    def addRow(DemonName, Item, Radius, Rage):
        data = MetalDetectorManager.SingleDetector(Item, Radius, Rage)
        MetalDetectorManager.detectors[DemonName] = data

    @staticmethod
    def hasDetector(DemonName):
        return DemonName in MetalDetectorManager.detectors

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
