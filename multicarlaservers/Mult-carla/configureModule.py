# ==================================================================================================
# -- imports ---------------------------------------------------------------------------------------
# ==================================================================================================

import logging

# ==================================================================================================
# -- import yaml ------------------------------------------------------------------------------------
# ==================================================================================================

import sys, os

import yaml

# ==================================================================================================
# -- configure ---------------------------------------------------------------------------------
# ==================================================================================================

class ConfigureModule(object):
    def __init__(self):
        ## 多服务器之间的进入/退出。需要服务器之间的确认，在双服务器的情况下先忽略
        self._servers_id = set()
        self._servers_IP = {}  # id:(host,port)
        self.subs = []

    def load_configure(self,path = "carlaservers.yaml"):
        with open(path,'r') as f:
            temp = yaml.load(f.read(), Loader=yaml.FullLoader)
            tempkeys = temp.keys()
            server_id = 0
            if 'sumo'in tempkeys :
                self._sumo = (temp['sumo']['host'],temp['sumo']['port'])
                host, port = self._sumo
                self._servers_IP[server_id] = (host, port)
                self._servers_id.add(server_id) 
                server_id += 1
            else:
                self._sumo = None
            # 添加服务器
            for s in temp['servers']:
                host = s['host']
                port = s['port']
                self._servers_IP[server_id] = (host,port)
                self._servers_id.add(server_id) 
                server_id += 1
                logging.info("Configure has been loaded, server: "+ host +":"+str(port) +".")
            if 'actorcolor'in tempkeys and temp['actorcolor'] in (True,1,"True","true"):
                self._actorcolor = True
            else:
                self._actorcolor = False
            if 'actorlights' in tempkeys and temp['actorlights'] in (True,1,"True","true"):
                self._actorlights = True
            else:
                 self._actorlights = False
            if 'trafficlights' in tempkeys and temp['trafficlights'] in (True,1,"True","true"):
                self._trafficlights = True
            else:
                self._trafficlights = False
            if 'weather' in tempkeys and temp['weather'] in (True,1,"True","true"):
                self._weather = True
            else:
                self._weather = False
            if 'steplength' in tempkeys and temp['steplength'] < 0.01:
                self._steplength = 0.05
            else:
                self._steplength = temp['steplength'] 
            logging.info("Configure sumo: {} ".format(self._sumo))
            logging.info("Configure actor color sync: {} ".format(self._actorcolor))
            logging.info("Configure actor lights sync: {} ".format(self._actorlights))
            logging.info("Configure traffic lights sync: {} ".format(self._trafficlights))
            logging.info("Configure weather sync:{}".format(self._weather))
            logging.info("Configure step length is:{}".format(self._steplength))


    def get_servers_id(self):
        """
            返回一个集合
        """
        return self._servers_id

    def get_servers_IP(self):
        """
            返回服务器ip字典
        """
        return self._servers_IP
    
    def get_step_length(self):
        """
            
        """
        return self._steplength

    def sync_traffic_lights(self):
        """
        
        """
        return self._trafficlights
    
    def sync_weather(self):
        return self._weather

    def sync_actor_color(self):
        return self._actorcolor
    
    def sync_actor_lights(self):
        return self._actorlights
    
    def get_sumo(self):
        return self._sumo
