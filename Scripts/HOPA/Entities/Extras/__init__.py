def onInitialize():
    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager

    EntityManager.importEntity("HOPA.Entities.Extras", "Extras")
    ObjectManager.importObject("HOPA.Entities.Extras", "Extras")

    EntityManager.importEntity("HOPA.Entities.Extras.ExtrasConcept", "ExtrasConcept")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasConcept", "ExtrasConcept")

    EntityManager.importEntity("HOPA.Entities.Extras.ExtrasWallpaper", "ExtrasWallpaper")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasWallpaper", "ExtrasWallpaper")

    EntityManager.importEntity("HOPA.Entities.Extras.ExtrasEnigma", "ExtrasEnigma")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasEnigma", "ExtrasEnigma")

    EntityManager.importEntity("HOPA.Entities.Extras.ExtrasMusic", "ExtrasMusic")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasMusic", "ExtrasMusic")

    EntityManager.importEntity("HOPA.Entities.Extras.ExtrasHOG", "ExtrasHOG")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasHOG", "ExtrasHOG")
    
    return True