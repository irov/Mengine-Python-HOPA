from Foundation.TaskManager import TaskManager
from HOPA.Enigma import Enigma


class ScopeEnigma(Enigma):
    def __init__(self):
        super(ScopeEnigma, self).__init__()
        self._scope_chain = None

    def _onFinalize(self):
        super(ScopeEnigma, self)._onFinalize()

        self._cancelScope()

    def _getScopeGroup(self):
        return None

    def _playEnigma(self):
        self._cancelScope()

        group = self._getScopeGroup()
        self._scope_chain = TaskManager.createTaskChain(Group=group, Repeat=True)
        with self._scope_chain as source:
            self._onScopePlay(source)

    def _onScopePlay(self, source):
        pass

    def _cancelScope(self):
        task_chain = self._scope_chain
        self._scope_chain = None
        if task_chain is not None:
            task_chain.cancel()
