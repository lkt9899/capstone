import traitlets


class Motor_car(traitlets.HasTraits):
    steering = traitlets.Float()
    throttle = traitlets.Float()
    
    @traitlets.validate('steering')
    def _clip_steering(self, proposal):
        if proposal['value'] > 1.0:
            return 1.0
        elif proposal['value'] < -1.0:
            return -1.0
        else:
            return proposal['value']
        
    @traitlets.validate('throttle')
    def _clip_throttle(self, proposal):
        if proposal['value'] > 1.0:
            return 1.0
        elif proposal['value'] < -1.0:
            return -1.0
        else:
            return proposal['value']
    
    def init_set(self) :
        # steering set
        self.steering_offset = -0.15
        self.steering = 0
        self.steering_gain = 0.65
        
        # throttle set
        self.throttle = 0
        self.throttle_gain = 0.45
