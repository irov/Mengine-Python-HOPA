from Foundation.DatabaseManager import DatabaseManager
from Foundation.System import System

class SystemFontCheckSymbols(System):
    def __init__(self):
        super(SystemFontCheckSymbols, self).__init__()
        pass

    def _loadLocales(self):
        records = DatabaseManager.getDatabaseRecords("Database", "FontCheckSymbols")

        currentLocale = Mengine.getLanguagePack()

        for record in records:
            Locale = record.get("Locale")
            Symbols = record.get("Symbols")

            if Locale == currentLocale:
                self._checkSymbols(Locale, Symbols)
                return
                pass
            pass

        Trace.log("System", 0, "Warning! No has symbols to locale [%s] in FontCheckSymbols.xlsx, please add!!" % (currentLocale))
        pass

    def _onRun(self):
        self._loadLocales()
        return True
        pass

    def _checkSymbols(self, locale, symbols):
        Fonts = []

        def __visitFonts(fontName):
            Fonts.append(fontName)
            pass

        Mengine.visitFonts(__visitFonts)

        for font in Fonts:
            if font == "__CONSOLE_FONT__":
                continue
                pass

            if Mengine.validateFont(font, symbols) is False:
                Trace.log("System", 0, "invalid font %s" % (font))
                pass
            pass
        pass
    pass