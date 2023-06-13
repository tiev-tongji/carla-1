# ==================================================================================================
# -- imports ---------------------------------------------------------------------------------------
# ==================================================================================================

import argparse
from locale import setlocale
import logging
import time

# ==================================================================================================
# -- find carla module -----------------------------------------------------------------------------
# ==================================================================================================

import glob
import os
import sys

from simplejson import load


try:
    sys.path.append(
        glob.glob('../PythonAPI/carla/dist/carla-*%d.%d-%s.egg' %
                  (sys.version_info.major, sys.version_info.minor,
                   'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla  # pylint: disable=import-error

# ==================================================================================================
# -- find carla simulation module -----------------------------------------------------------------------------
# ==================================================================================================


# 1. information tranfromation module

# 2. network and configure module

class SynchronizeModule(object):
    def __init__(self, configure):
        self.carlaList = []
        self.configure = configure
        self.load_servers()

        self.actors = set() # （carlaIndex,actorId）:actor


        # Configuring carla simulation in sync mode.
        settings = self.carla.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = self.carla.step_length
        self.carla.world.apply_settings(settings)

        traffic_manager = self.carla.client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
        
    def add_carla(self, carla_simulation):
        pass

    def remove_carla(self,carla_simulation):
        pass

    ##涉及 carlaSimulation 模块
    def load_servers(self):
        carlaId = self.configure.get_servers_id()
        carlaIP = self.configure.get_servers_IP()
        for id in carlaId:
            host,port = carlaIP[id]
            carla = (host,port)
            self.carlaList.append(carla)   
            logging.info("Carla has been loaded, server: "+ host +":"+str(port) +" .")

    def update_configure(self,configure):
        self.configure = configure
        self.load_servers()

    def set_weather(self):
        pass

    def joint_actors(self):
        pass


    def joint_info(self):
        """
        Tick to simulation synchronization
        """
        #actors
        for carlaIndex,carla in enumerate(self.carlaList):
            carla.tick()
            carla_spawned_actors = self.actors # self.carla.spawned_actors
            



        #traffic lights

    def tick(self):
        pass

    def get_carla_lights_state(self):
        pass
