def onInitialize():
    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager
    from Foundation.TaskManager import TaskManager

    ObjectManager.importObject("HOPA.Entities.InventoryFX", "InventoryFX")
    EntityManager.importEntity("HOPA.Entities.InventoryFX", "InventoryFX")

    InvFXTasks = ["TaskInventoryFXAddItem"]
    TaskManager.importTasks("HOPA.Entities.InventoryFX", InvFXTasks)
    
    return True