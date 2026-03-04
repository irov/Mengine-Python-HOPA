def onInitialize():
    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager
    from Foundation.TaskManager import TaskManager

    EntityManager.importEntity("HOPA.Entities.Reagents", "Reagents")
    ObjectManager.importObject("HOPA.Entities.Reagents", "Reagents")

    EntityManager.importEntity("HOPA.Entities.Reagents.ReagentsEnigma", "ReagentsEnigma")
    ObjectManager.importObject("HOPA.Entities.Reagents.ReagentsEnigma", "ReagentsEnigma")

    EntityManager.importEntity("HOPA.Entities.Reagents.ReagentsButton", "ReagentsButton")
    ObjectManager.importObject("HOPA.Entities.Reagents.ReagentsButton", "ReagentsButton")

    TaskManager.importTask("HOPA.Entities.Reagents.Macro", "AliasPickReagentPaper")