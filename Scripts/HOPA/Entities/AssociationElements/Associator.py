class Associator(object):
    def __init__(self, secretInstances):
        self.secrets = secretInstances
        pass

    def isComplete(self):
        for secret in self.secrets:
            if secret.getClassified() is True:
                continue
            return False
        return True

    def isMine(self, secret):
        return secret in self.secrets
        pass

    def unclassified(self):
        for secret in self.secrets:
            if secret.getClassified() is True:
                secret.toSecret()
            pass
        pass

    def classified(self):
        for secret in self.secrets:
            secret.toClassified()
            pass
        pass

class SecretManagement(object):

    def __init__(self):
        self.associations = {}
        self.bufferAssociate = None
        pass

    def associate(self, secretsListOfTuples):
        for secretsPairTuple in secretsListOfTuples:
            AssociatorInst = Associator(secretsPairTuple)
            [self.associations.update({secretInst: AssociatorInst}) for secretInst in secretsPairTuple]
            pass
        pass

    def push(self, secretInst):
        secretInst.toClassified()
        if self.bufferAssociate is None:
            self.bufferAssociate = self.associations.get(secretInst)
            return
            pass
        else:
            associator = self.associations.get(secretInst)
            if associator is self.bufferAssociate:
                if associator.isComplete() is False:
                    return
                    pass
            else:
                self.bufferAssociate.unclassified()
                associator.unclassified()
                pass
            self.bufferAssociate = None
            pass
        return

    def isComplete(self):
        state = [assoc.isComplete() for assoc in self.associations.values()]
        completeState = set(state)
        if False in completeState:
            return False
            pass
        return True