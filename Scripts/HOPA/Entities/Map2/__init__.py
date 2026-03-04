def onInitialize():
    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager

    EntityManager.importEntity("HOPA.Entities.Map2", "Map2")
    ObjectManager.importObject("HOPA.Entities.Map2", "Map2")

    EntityManager.importEntity("HOPA.Entities.Map2.OpenMap", "OpenMap")
    ObjectManager.importObject("HOPA.Entities.Map2.OpenMap", "OpenMap")

    EntityManager.importEntity("HOPA.Entities.Map2.MapSwitch", "MapSwitch")
    ObjectManager.importObject("HOPA.Entities.Map2.MapSwitch", "MapSwitch")

    EntityManager.importEntity("HOPA.Entities.Map2.CollectedMap", "CollectedMap")
    ObjectManager.importObject("HOPA.Entities.Map2.CollectedMap", "CollectedMap")

    EntityManager.importEntity("HOPA.Entities.Map2.CollectedMapIndicator", "CollectedMapIndicator")
    ObjectManager.importObject("HOPA.Entities.Map2.CollectedMapIndicator", "CollectedMapIndicator")