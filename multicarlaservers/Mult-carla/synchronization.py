
# ==================================================================================================
# -- imports ---------------------------------------------------------------------------------------
# ==================================================================================================

import argparse
import logging
import time

# ==================================================================================================
# -- find carla module -----------------------------------------------------------------------------
# ==================================================================================================

import glob
import os
import sys
import random
import threading
import copy

from constants import INVALID_ACTOR_ID

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

from carlaSimulation import CarlaSimulation
from configureModule import ConfigureModule
from logModule import CustomFormatter

class SimulationSynchronization(object):

    class ServerError(Exception):
        def __init__(self):
            pass

    def __init__(self,
                 carla_list,
                 sync_vehicle_color=False,
                 sync_vehicle_lights=False,
                 sync_traffic_lights= False,
                 sync_weather= False):

        self.carla_list = carla_list
        self.sync_vehicle_color = sync_vehicle_color
        self.sync_vehicle_lights = sync_vehicle_lights
        self.sync_traffic_lights = sync_traffic_lights
        self.sync_weather = sync_weather

        # multithread related
        self.lock = threading.Lock()
        self.thread_list =[] 
        # id list 
        self.actor_store = {} # 结构是carla_id : {actor_id:actor,,,}
        for cl in self.carla_list:
            actor_dict = {}
            self.actor_store[cl.id] = actor_dict
        # blueprint library
        # self.blueprint_libraries = {} # carla_id : blueprint_library

        # ☆★get blueprint_library and map in every world 
        self.sim_map = None
        logging.info('start to update blueprint_library updated and verify map.')
        for cl in self.carla_list:
            # blueprint part
            """
            logging.debug('start to get blueprint library of server {}.'.format(cl.id))
            self.blueprint_libraries[cl.id] = cl.world.get_blueprint_library()
            logging.debug('Done! got blueprint library of server {}.'.format(cl.id))
            """
            # map part: ensure map identical
            sim_hash = None
            try:
                logging.debug('start to get map of server {}.'.format(cl.id))
                clh = cl.map_hash
                if not sim_hash:
                    sim_hash = clh
                else:
                    if sim_hash != clh:
                        raise self.ServerError
            except RuntimeError as error:
                logging.error('RuntimeError: {}'.format(error))
                logging.error(' Server {} has an error.'.format(cl.id))
                logging.error('  The server could not send the OpenDRIVE (.xodr) file:')
                logging.error('  Make sure it exists, has the same name of your town, and is correct.')
            except self.ServerError:
                logging.error('ServerError: Maps on servers are not identical.')
                logging.error(' Server {} has a different map.'.format(cl.id))
                logging.error(' The map on each server should be identical:')
                logging.error(' Copy a map to all servers and ensure worlds have changed into the same map.')
        logging.info('Done! blueprint_library updated and map is verified.')
  

        # ☆★ start simulation, set carla simulation in sync mode.
        settings = None
        logging.info('start to set synchronous mode.')
        for cl in self.carla_list:
            if not settings:
                settings = cl.world.get_settings()
                settings.synchronous_mode = False
                settings.fixed_delta_seconds = cl.step_length
            cl.world.apply_settings(settings)
            traffic_manager = cl.client.get_trafficmanager()
            traffic_manager.set_synchronous_mode(False)
        logging.info('Done! Synchronous mode has been setted.')



    
    def _get_recommend_blueprint(self, carla_id, actor_ontology):
        """
        Get a random blurprint.
        """
        logging.debug('begin to select a random blueprint.')
        filterWord = {4:"walker.*", 10:"vehicle.*", 12:"待修改TrafficSign", 18:"待修改TrafficLight"}
        logging.warning('TODO! blueprint tags need to change.')       
        filter_tags = filterWord.keys()
        actor_tags = actor_ontology.semantic_tags
        blueprint = None
        for t in actor_tags:
            if t in filter_tags:
                blueprint = random.choice(self.carla_list[carla_id].blueprint_library.filter(filterWord[t]))
                break
        return blueprint
        
    def _get_actor_store(self):
        actor_store_copy = None
        if self.lock.acquire():
            actor_store_copy = copy.deepcopy(self.actor_store)
            self.lock.release()
        return actor_store_copy

    @staticmethod
    def get_all_avatars(avatars_dict):
        result = set()
        for s in avatars_dict.values():
            in_ids = set([id_inworld for id_inworld, _ in s])
            result = result | in_ids
        return result

    def update_actors(self, carlalet):
        """
        Update all actor information of carla.
        """
        carlalet.update_info()
        # update store from carlalet
        logging.info('start to update actors of server {}.'.format(carlalet.id))
        if True:
            # in_world放的actor，ofWorld放的id,
            # actor 只用关注 载具，行人，交通灯
            actors_in_world = carlalet.get_actors() #.NET
            vehicles_in_world = actors_in_world.filter('vehicle.*')
            walkers_in_world = actors_in_world.filter('walker.*')
            ## 更新 store
            # 获取actor_store中存在的该世界的actors
            actors_ofWorld = set(
                [vehicle.id for vehicle in vehicles_in_world] + 
                [walker.id for walker in walkers_in_world ] )
            # 数据准备 inworld - avatar => ontology
            carlalet.ontology = actors_ofWorld - self.get_all_avatars(carlalet.avatars)
            ontology_store_dict = self.actor_store[carlalet.id] # ^^^ # {actor_id : actor}  
            ontology_ofStore = set(ontology_store_dict.keys()) 
            actor_add2Store = carlalet.ontology - ontology_ofStore
            actor_del2Store = ontology_ofStore - carlalet.ontology
            actor_upd2Store = carlalet.ontology & ontology_ofStore
            logging.debug('#{}:当前世界的actor SET:{}.'.format(carlalet.id,actors_ofWorld))
            logging.debug('#{}:当前世界的ontology SET:{}.'.format(carlalet.id,carlalet.ontology))
            logging.debug('#{}:原记录中的ontology SET:{}.'.format(carlalet.id,ontology_ofStore))
            logging.debug('#{}:需要增加的ontology记录 SET:{}.'.format(carlalet.id,actor_add2Store))
            logging.debug('#{}:需要删除的ontology记录 SET:{}.'.format(carlalet.id,actor_del2Store))
            logging.debug('#{}:需要更新的ontology记录 SET:{}.'.format(carlalet.id,actor_upd2Store))
            # 新建角色 ontology.actor not in store-forThisWorld, add to store.actor 
            for actor_id_inworld in actor_add2Store:
                ###重点@！ 不应该存角色 应该存角色的数据 比如transform，light，color 和typeid，
                ontology_store_dict[actor_id_inworld] = carlalet.get_actor(actor_id_inworld) # ^^^
                logging.debug('#{}:actor信息:{}.'.format(carlalet.id,ontology_store_dict[actor_id_inworld]))
                carlalet.ontology.add(actor_id_inworld)
                logging.debug('ontology {} is added to store.'.format(actor_id_inworld))            
            # 删除角色 store.actor-forThisWorld！ not in ontology, delete store.actor
            for actor_id_inworld in actor_del2Store:
                ontology_store_dict.pop(actor_id_inworld) # ^^^
                carlalet.ontology.discard(actor_id_inworld)
                logging.debug('ontology {} is deleted from store.'.format(actor_id_inworld))
            # 更新角色 update ontology.actor.transform... to store.actor.transformation
            for actor_id_inworld in actor_upd2Store:
                new_transform = carlalet.get_actor(actor_id_inworld).get_transform()
                ontology_store_dict[actor_id_inworld].set_transform(new_transform) # ^^^
                logging.debug('ontology {} is updated to store.'.format(actor_id_inworld))
        logging.info('Server {} Update Store has been done.'.format(carlalet.id))
        
        # update carlalet from store 
        ## 循环遍历carlalist 对其中每一个
        logging.info('start to update avater of server {}.'.format(carlalet.id))
        if carlalet.isSumo:
            logging.info('skip update avater of sumo {}.'.format(carlalet.id))
            return True

        if logging.getLevelName(logging.getLogger()) =="Debug":
            newavatar_ofWorld = set()
            newavatar_ofStore = set()
            newavatar_spawning = set()
            newavatar_destroying = set()
            newavatar_updating = set()

        for cl in self.carla_list:
            if cl.id == carlalet.id:
                continue
            else:
                if cl.id not in carlalet.avatars:# 若没有该世界的avatar
                    carlalet.avatars[cl.id]= set() #（id_inworld， id_onworld）
                avatars_in_world = carlalet.avatars[cl.id]
                avatar_ofWorld = set([id_onworld for _ ,id_onworld in avatars_in_world])
                actors_info = self.actor_store[cl.id]
                avatar_ofStore = set(actors_info.keys()) # ^^^
                avatar_spawning = avatar_ofStore - avatar_ofWorld
                avatar_destroying = avatar_ofWorld - avatar_ofStore
                avatar_updating = avatar_ofStore & avatar_ofWorld
                avatar_destroying_ids= [(id_inworld,id_onWorld) for id_inworld , id_onWorld in avatars_in_world if id_onWorld in avatar_destroying]
                avatar_updating_ids = [(id_inworld,id_onWorld) for id_inworld , id_onWorld in avatars_in_world if id_onWorld in avatar_updating]
                logging.debug('#{}:原世界中的avatar SET:{}.'.format(carlalet.id,avatar_ofWorld))
                logging.debug('#{}:原记录中的avatar SET:{}.'.format(carlalet.id,avatar_ofStore))
                logging.debug('#{}:需要创建的avatar SET:{}.'.format(carlalet.id,avatar_spawning))
                logging.debug('#{}:需要销毁的avatar SET:{}.'.format(carlalet.id,avatar_destroying))
                logging.debug('#{}:需要更新的avatar SET:{}.'.format(carlalet.id,avatar_updating))
                # 新建角色 store[clid] - avatars[clid], spawn the avatar(actor), and add avatar
                for actor_id_onWorld in avatar_spawning:
                    # self.actor_store[carlalet.id] 
                    actor_onWorld = actors_info[actor_id_onWorld]
                    logging.debug('#{}:actor信息:{}.'.format(carlalet.id,actor_onWorld))
                    
                    blueprint_onWorld = actor_onWorld.type_id
                    transform_onWorld = actor_onWorld.get_transform()
                    logging.debug('角色id信息是 :{}.'.format(blueprint_onWorld))
                    logging.debug('角色位置是 :{}.'.format(transform_onWorld.location))
                    logging.debug('角色方向是 :{}.'.format(transform_onWorld.rotation))
                    blueprint = cl.blueprint_library.find(blueprint_onWorld)
                    transform_onWorld.location.z += 1.2
                    logging.debug('获得的蓝图是 :{}.'.format(blueprint))
                    logging.debug('新位置是 :{}.'.format(transform_onWorld.location))
                    if not blueprint:
                        logging.warning("Blueprint of {} hasn't been found in server {}.".format(cl.id, carlalet.id))
                        logging.warning("A random actor generated as a subtitute.")
                        blueprint = self._get_recommend_blueprint(carlalet.id, actor_onWorld)
                    if blueprint.has_attribute('color') and self.sync_vehicle_color :
                        color = actor_onWorld.attributes.get('color',None)
                        blueprint.set_attribute('color',color)
                    avatar_id_inWorld = carlalet.spawn_actor(blueprint,transform_onWorld)
                    if avatar_id_inWorld != INVALID_ACTOR_ID:
                        carlalet.avatars[cl.id].add((avatar_id_inWorld, actor_id_onWorld))
                        logging.debug('new avatar spawned. |B|')
                # 删除角色 avatars[clid] - store[clid], delete the actor
                for id_pair in avatar_destroying_ids:
                    id_inWorld, _ = id_pair
                    carlalet.destroy_actor(id_inWorld) #NET
                    avatars_in_world.discard(id_pair)
                    logging.debug('avatar {} is destoried.'.format(id_inWorld))
                # 更新角色 update avators.actor.transformation from store
                for id_pair in avatar_updating_ids:
                    id_inWorld, id_onWorld = id_pair
                    actor_onWorld =actors_info[id_onWorld] 
                    transform_onWorld = actor_onWorld.get_transform()
                    vehicle_light_onWorld =  actor_onWorld.get_light_state() if self.sync_vehicle_lights else None
                    carlalet.synchronize_vehicle(id_inWorld,transform_onWorld,vehicle_light_onWorld) #NET
                    # carlalet.get_actor(id_inWorld).set_transform(transform_onWorld)
                    logging.debug('avatar {} is updated.'.format(id_pair))
                logging.debug('Server {} to Server {} updated.'.format(cl.id, carlalet.id))
                if logging.getLevelName(logging.getLogger()) =="Debug":
                    newavatar_ofWorld = newavatar_ofWorld | set([id_onworld for _ ,id_onworld in avatars_in_world])
                    newavatar_ofStore = newavatar_ofStore | set(self.actor_store[cl.id].keys()) # ^^^
                    newavatar_spawning = newavatar_spawning | (avatar_ofStore - avatar_ofWorld)
                    newavatar_destroying = newavatar_destroying | (avatar_ofWorld - avatar_ofStore)
                    newavatar_updating = newavatar_updating | (avatar_ofStore & avatar_ofWorld)
                    logging.debug('#{}:当前世界的avatar SET:{}.'.format(carlalet.id,newavatar_ofWorld))
                    logging.debug('#{}:当前记录的avatar SET:{}.'.format(carlalet.id,newavatar_ofStore))
                    logging.debug('#{}:需要创建的avatar SET:{}.'.format(carlalet.id,newavatar_spawning))
                    logging.debug('#{}:需要销毁的avatar SET:{}.'.format(carlalet.id,newavatar_destroying))
                    logging.debug('#{}:需要更新的avatar SET:{}.'.format(carlalet.id,newavatar_updating))
        
        if logging.getLevelName(logging.getLogger()) =="Debug":
            logging.debug('当前世界的avatar SET:{}.'.format(newavatar_ofWorld))
            logging.debug('当前记录的avatar SET:{}.'.format(newavatar_ofStore))
            logging.debug('需要创建的avatar SET:{}.'.format(newavatar_spawning))
            logging.debug('需要销毁的avatar SET:{}.'.format(newavatar_destroying))
            logging.debug('需要更新的avatar SET:{}.'.format(newavatar_updating))

            logging.debug('----------------------- -----------------------')
        logging.info('Server {} Update Carla has been done.'.format(carlalet.id))


    def update_traffic_light(self):
        common_landmarks = self.carlalet.traffic_light_ids
        for landmark_id in common_landmarks:
            tl_state = self.carlalet.get_traffic_light_state(landmark_id)
            
            self.carla.synchronize_traffic_light(landmark_id, tl_state)

    def update_weather(self):
        pass

    def update_status(self,carlalet):
        logging.debug('start to update status in carla {}.'.format(carlalet.id))
        try:
            if self.lock.acquire():# it could be optimized here!
                logging.debug('@@@@@@@@ Lock @@@@@@@@@ carla {} locked!'.format(carlalet.id))
                self.update_actors(carlalet)
                self.lock.release()
                logging.debug('######## Unlock ######## carla {} released!'.format(carlalet.id))
            carlalet.tick()
            logging.debug('done! carla {} ticked.'.format(carlalet.id))
        except KeyboardInterrupt:
            if self.lock.locked:
                self.lock.release()
            logging.info('Cancelled by user.')
        finally:
            logging.info('Cleaning threading')

    def update_environment(self):
        if self.sync_traffic_lights:
            self.update_traffic_light()
        if self.sync_weather:
            self.update_weather()

    def tick(self):
        """
        Tick to simulation synchronization
        """
        for carlalet in self.carla_list:
            #sync actors ( Todo consider vehicle lights and color)
            t =threading.Thread(target = self.update_status,args = (carlalet,))
            logging.debug('thread has been created for carla {}.'.format(carlalet.id))
            self.thread_list.append(t)
        
        t = threading.Thread(target = self.update_environment)
        self.thread_list.append(t)

        for t in self.thread_list:
            logging.debug('thread {} start.'.format(t))
            t.start()
        for t in self.thread_list:
            t.join()
        self.thread_list.clear()
        logging.debug('tick for threads finished.')


    def close(self):
        """
        Cleans synchronization.
        """
        logging.debug('begin to close carla.')
        for carlalet in self.carla_list:
            # Configuring carla simulation in async mode.
            settings = carlalet.world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            carlalet.world.apply_settings(settings)
        
            # Closing sumo and carla client.
            carlalet.close()
            logging.debug('carla {} closed.'.format(carlalet.id))



def synchronization_loop():
    """
    Entry point for co-simulation.
    """
    # 加载配置
    conf = ConfigureModule()
    conf.load_configure()
    servers_list = conf.get_servers_id()
    servers_address = conf.get_servers_IP()
    step_length = conf.get_step_length()
    # 尝试连接
    carla_list =[]
    # ##先只尝试2～3个服务器，则对内存负担不高。优化可增加缓存
    for server_id in servers_list:           
        host, port = servers_address[server_id]
        logging.debug('start to connect Carla {}:{}'.format(host, port))            
        try:
            carlalet = CarlaSimulation(host, port,step_length , server_id)
            if server_id == 0 and conf.get_sumo():
                carlalet.isSumo = True
                logging.info('Connect SUMO {}:{}.'.format(host, port))
        except Exception as er:
            logging.error("Failed! Can't connect Carla {}:{}".format(host,port))
            logging.error("Error: {}".format(er))
        finally:
            logging.info('Done! connect Carla {}:{} finished.'.format(host, port))
        logging.debug('end to connect Carla {}:{}'.format(host, port))
        carla_list.append(carlalet)
     
    # 初始化同步模块
    synchronization = SimulationSynchronization(carla_list,\
                conf.sync_actor_color(), conf.sync_actor_lights(),\
                conf.sync_traffic_lights(), conf.sync_weather())
    
    # 删除配置模块--
    del conf

    try:
        while True:
            start = time.time()

            synchronization.tick()

            end = time.time()
            elapsed = end - start
            if elapsed < step_length :
                time.sleep(step_length  - elapsed)
            logging.info('ticked.')

    except KeyboardInterrupt:
        logging.info('Cancelled by user.')

    finally:
        logging.info('Cleaning synchronization')

        synchronization.close()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('--debug', action='store_true', help='enable debug messages')
    arguments = argparser.parse_args()

    # create logger with 'spam_application'
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    if arguments.debug:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    synchronization_loop()
