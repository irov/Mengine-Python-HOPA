import Trace

class MacroCommandFactory(object):
    s_commandType = {}
    s_commandEnumerator = 0

    @staticmethod
    def addCommandType(name, commandType):
        MacroCommandFactory.s_commandType[name] = commandType
        pass

    @staticmethod
    def newCommandID():
        MacroCommandFactory.s_commandEnumerator += 1

        return MacroCommandFactory.s_commandEnumerator
        pass

    @staticmethod
    def createCommand(commandTypeName):
        if commandTypeName not in MacroCommandFactory.s_commandType:
            Trace.log("Macro", 0, "MacroCommandFactory.createCommand not found commandType %s" % (commandTypeName))
            return None
            pass

        CommandType = MacroCommandFactory.s_commandType[commandTypeName]

        Command = CommandType()

        commandId = MacroCommandFactory.newCommandID()
        Command.setCommandId(commandId)
        Command.setCommandType(commandTypeName)

        return Command
        pass
    pass