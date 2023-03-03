class Connectable:
    square_error = 15
    EMITTER = 1
    RECEIVER = 0

    def __init__(self, input, outputs, flowInst):
        self.input = input
        self.outputs = outputs
        self.emitting = False
        self.connected_from = None
        self.flow = flowInst
        self.type = None
        pass

    def markAsSource(self):
        self.emitting = True
        #        input_posa = self.input.getWorldPosition()

        self.flow.higlight(self.input)
        pass

    def setAsSource(self):
        self.type = Connectable.EMITTER
        self.markAsSource()
        pass

    def setAsReceiver(self):
        self.type = Connectable.EMITTER
        pass

    def removeEmitter(self):
        if self.type is Connectable.EMITTER:
            return

        self.emitting = False
        pass

    def is_emitting(self):
        return self.emitting
        pass

    def getOutputs(self):
        if self.emitting is False:
            return []
        else:
            return self.outputs
        pass

    def getInput(self):
        return self.input
        pass

    def does_join(self, foreignInputNode):
        foreignInput = foreignInputNode.getWorldPosition()
        s_outputs_nodes = self.getOutputs()
        #        s_outputs = [out.getWorldPosition() for out in s_outputs_nodes]
        for s_output in s_outputs_nodes:
            s_out = s_output.getWorldPosition()
            dx = s_out[0] - foreignInput[0]
            dy = s_out[1] - foreignInput[1]
            square_distance = (dx ** 2 + dy ** 2) ** .5
            if square_distance < Connectable.square_error:
                self.flow.higlight(s_output)
                return True
                pass
        return False
        pass

    def rebound(self, connectableInstance):
        if connectableInstance is self:
            return False
            pass
        if self.emitting is False or connectableInstance.is_emitting():
            return False
            pass
        foreignInputNode = connectableInstance.getInput()
        if self.does_join(foreignInputNode) is True:
            self.connected_from = connectableInstance
            connectableInstance.markAsSource()
            return True
            pass
        return False
        pass

    def is_connected(self):
        if self.connected_from is None:
            return False
        return True
        pass


class Connections(object):

    def __init__(self, movie, connections, topLevelConnections=None):
        self.movie = movie
        self.connections = connections
        self.connectables = []
        self.topLevelConnections = topLevelConnections
        self._onInitialize()
        pass

    def setTop(self, topConnectionsInstance):
        self.topLevelConnections = topConnectionsInstance

    def _onInitialize(self):
        for input, outputs in self.connections.items():
            connectable = Connectable(input, outputs)
            self.connectables.append(connectable)
            pass
        pass

    def getConnectables(self):
        return self.connectables
        pass

    def shift(self):
        if self.topLevelConnections is None:
            return
        foreign_connectables = self.topLevelConnections.getConnectables()
        for connectable in self.connectables:
            for foreign_conn in foreign_connectables:
                foreign_conn.rebound(connectable)
                pass
            pass
        pass

    def getConnectedNodes(self):
        connected = [conn for conn in self.connectables if conn.is_connected()]
        return connected
        pass
