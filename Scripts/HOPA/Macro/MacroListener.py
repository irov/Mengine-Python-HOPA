from HOPA.Macro.MacroCommand import MacroCommand

class MacroListener(MacroCommand):
    SKIP_SIGN = "__"

    def _onValues(self, values):
        self.notifyID = Notificator.getIdentity(values[0])
        self.user_args = [val for val in values[1:]]  # values with '#' ignores by xlsxExporter

    def __filter(self, *args):
        for user_arg, input_arg in zip(self.user_args, args):
            # skip if arg is skip sign (use for comments etc)
            if user_arg == MacroListener.SKIP_SIGN:
                continue

            # try to compare with right type
            if isinstance(input_arg, float) and isinstance(user_arg, int):
                user_arg = float(user_arg)
            elif isinstance(input_arg, bool) and isinstance(user_arg, int):
                user_arg = bool(user_arg)
            # todo: make right check with None value

            if user_arg != input_arg:
                return False
        return True

    def _onGenerate(self, source):
        source.addTask("TaskListener", ID=self.notifyID, Filter=self.__filter)