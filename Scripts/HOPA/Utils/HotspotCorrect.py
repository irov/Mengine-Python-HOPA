def HotspotCorrect(hotspot, group, filter):
    hss = []

    def __getHotspot(obj):
        hs = filter(obj)

        if hs is None:
            return True
            pass

        if hs is hotspot:
            return False
            pass

        hss.append(hs)

        return True
        pass

    if group.visitObjects2(__getHotspot) is True:
        return []
        pass

    if len(hss) == 0:
        return []
        pass

    p = Mengine.hotspotCorrect(hotspot, hss)

    return p
    pass
