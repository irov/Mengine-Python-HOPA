from Foundation.DatabaseManager import DatabaseManager


class ColoringPuzzleManager(object):
    s_games = {}

    class ColoringPuzzleGame(object):
        def __init__(self, brushes, fragments, coloringRules, palette, colors, brushesToColor, startColorId):
            self.brushes = brushes
            self.fragments = fragments
            self.coloringRules = coloringRules
            self.palette = palette
            self.colors = colors
            self.brushesToColor = brushesToColor
            self.startColorId = startColorId

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            Brushes = record.get("Brushes")
            BrushesToColor = record.get("BrushesToColor")
            ColoringRules = record.get("ColoringRules")
            Colors = record.get("Colors")
            Fragments = record.get("Fragments")
            Palette = record.get("Palette")
            StartColorId = record.get("StartColorId")

            ColoringPuzzleManager.loadGame(module, Name, StartColorId, Brushes, ColoringRules, Fragments, Palette,
                                           Colors, BrushesToColor)
            pass

        return True
        pass

    @staticmethod
    def loadGame(module, name, StartColorId, BrushesParam, ColoringRulesParam, FragmentsParam, PaletteParam,
                 ColorsParam, BrushesToColorParam):
        brushes = ColoringPuzzleManager.loadGameBrushes(module, BrushesParam)
        fragments = ColoringPuzzleManager.loadGameFragments(module, FragmentsParam)
        coloringRules = ColoringPuzzleManager.loadGameColoringRules(module, ColoringRulesParam)
        palette = ColoringPuzzleManager.loadGamePalette(module, PaletteParam)
        colors = ColoringPuzzleManager.loadGameColors(module, ColorsParam)
        brushesToColor = ColoringPuzzleManager.loadGameBrushesToColor(module, BrushesToColorParam)

        game = ColoringPuzzleManager.ColoringPuzzleGame(brushes, fragments, coloringRules, palette, colors,
                                                        brushesToColor, StartColorId)

        ColoringPuzzleManager.s_games[name] = game
        return game
        pass

    @staticmethod
    def loadGameBrushes(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        brushes = {}
        for record in records:
            brushId = record.get("BrushId")
            objectName = record.get("ObjectName")
            groupName = record.get("GroupName")
            brushes[brushId] = dict(ObjectName=objectName, GroupName=groupName)
            pass
        return brushes
        pass

    @staticmethod
    def loadGameColors(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        colors = {}
        for record in records:
            colorName = record.get("ColorName")
            colorId = record.get("ColorId")
            colors[colorId] = dict(ColorName=colorName)
            pass
        return colors
        pass

    @staticmethod
    def loadGameFragments(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        fragments = {}
        for record in records:
            fragmentId = record.get("FragmentId")
            defaultColorId = record.get("DefaultColorId")
            objectName = record.get("ObjectName")
            socketObjectName = record.get("SocketObjectName")
            fragments[fragmentId] = dict(ObjectName=objectName, SocketObjectName=socketObjectName, DefaultColorId=defaultColorId)
        return fragments

    @staticmethod
    def loadGameColoringRules(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        coloringRules = {}
        for record in records:
            fragmentId = record.get("FragmentId")
            colorId = record.get("ColorId")
            coloringRules[fragmentId] = colorId
            pass
        return coloringRules
        pass

    @staticmethod
    def loadGamePalette(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        palette = {}
        for record in records:
            paletteId = record.get("PaletteId")
            colorId = record.get("ColorId")
            socketObjectName = record.get("SocketObjectName")
            palette[paletteId] = dict(SocketObjectName=socketObjectName, ColorId=colorId)
            pass
        return palette
        pass

    @staticmethod
    def loadGameBrushesToColor(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        brushesToColor = {}
        for record in records:
            brushId = record.get("BrushId")
            colorId = record.get("ColorId")
            brushesToColor[colorId] = brushId
            pass
        return brushesToColor
        pass

    @staticmethod
    def getGame(name):
        if name not in ColoringPuzzleManager.s_games:
            Trace.log("Manager", 0, "ColoringPuzzleManager.getGame: not found game %s" % (name))
            return None
            pass
        game = ColoringPuzzleManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in ColoringPuzzleManager.s_games
