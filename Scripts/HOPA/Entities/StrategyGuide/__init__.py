def onInitialize():
    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager

    EntityManager.importEntity("HOPA.Entities.StrategyGuide.StrategyGuideMenu", "StrategyGuideMenu")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuideMenu", "StrategyGuideMenu")

    EntityManager.importEntity("HOPA.Entities.StrategyGuide.StrategyGuideZoom", "StrategyGuideZoom")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuideZoom", "StrategyGuideZoom")

    EntityManager.importEntity("HOPA.Entities.StrategyGuide.StrategyGuidePage", "StrategyGuidePage")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuidePage", "StrategyGuidePage")

    EntityManager.importEntity("HOPA.Entities.StrategyGuide.StrategyGuideController", "StrategyGuideController")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuideController", "StrategyGuideController")
    
    return True
