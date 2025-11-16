def HotspotCorrect(hotspot, group, filter):
    hss = []

    def __getHotspot(obj):
        hs = filter(obj)

        if hs is None:
            return True

        if hs is hotspot:
            return False

        hss.append(hs)

        return True

    if group.visitObjectsBreakOnFalse(__getHotspot) is True:
        return []

    if len(hss) == 0:
        return []

    p = Mengine.hotspotCorrect(hotspot, hss)

    return p
