
class location(object):
    def __init__(self,location):
        self.x = location.x
        self.y = location.y
        self.z = location.z

class rotation(object):
    def __init__(self,rotation):
        self.yaw = rotation.yaw
        self.roll = rotation.roll
        self.pitch = rotation.pitch 

class transformation(object):
    def __init__(self,location=None,rotation=None):
        self.location = location
        self.rotation = rotation

class actor(object):
    def __init__(self,transformation=None,light_state=None,blueprint=None):
        self.transformation = transformation
        self.light_state = light_state
        self.blueprint = blueprint
    
        
class traffic_lights(object):
    def __init__(self):
        pass

class weather_setting(object):
    def __init__(self):
        pass

class map_setting(object):
    def __init__(self) -> None:
        pass    

class world_setting(object):
    def __init__(self) -> None:
        pass

class packer():
    def pack_actor(x,y,z,yaw,roll,pitch):
        pass

    