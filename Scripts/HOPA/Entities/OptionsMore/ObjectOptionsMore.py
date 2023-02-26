from Foundation.Object.DemonObject import DemonObject

class ObjectOptionsMore(DemonObject):
    def _onParams(self, params):
        super(ObjectOptionsMore, self)._onParams(params)

        # DefaultAccountFullscreen = DefaultManager.getDefaultFloat('DefaultAccountFullscreen', 0.5)

        self.params['Arrow'] = params.get('Arrow', False)
        # self.params['FullScreen'] = params.get('FullScreen', DefaultAccountFullscreen)
        self.params['WideScreen'] = params.get('WideScreen', False)