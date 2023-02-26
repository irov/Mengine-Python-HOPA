class BallStack(object):
    """
    Logic of view ball-shoot in the gun
    """
    state_obj = None
    states = None
    current_state = None
    final_state = None
    step = None

    @staticmethod
    def init_with(movieObject, states=3):
        BallStack.state_obj = movieObject
        BallStack.states = states
        BallStack.current_state = 1
        BallStack.final_state = movieObject.getDuration()
        BallStack.step = (BallStack.final_state - BallStack.current_state) / 3

        pass

    @staticmethod
    def turn_state():
        MovieEn = BallStack.state_obj.getEntity()
        _from = BallStack.current_state
        _to = BallStack.current_state + BallStack.step
        BallStack.current_state = _to
        if _to >= BallStack.final_state:
            BallStack.current_state = 0
            pass

    #        with TaskManager.createTaskChain() as tc:
    #            tc.addTask("TaskFunction", Fn = MovieEn.setTiming, Args=(_from,) )
    #            tc.addTask("TaskFunction", Fn = MovieEn.setInterval, Args=(_from,_to ) )
    #            tc.addTask("TaskMoviePlay", Movie = BallStack.state_obj, Wait = True)
    #            tc.addTask("TaskFunction", Fn = MovieEn.setInterval, Args=(0,BallStack.final_state-1) )
    #            tc.addTask("TaskFunction", Fn = MovieEn.setTiming, Args=(_to,) )
    #        pass

    @staticmethod
    def get():
        if BallStack.state_obj:
            state_entity = BallStack.state_obj.getEntity()
            return state_entity
        pass

    @staticmethod
    def reset():
        MovieEn = BallStack.state_obj.getEntity()
        MovieEn.setTiming(1)
        pass