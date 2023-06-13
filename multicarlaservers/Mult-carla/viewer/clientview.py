#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import glob
import os
import sys
import time 
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla



def get_transform(transform, d=6.4):
    location = carla.Location(2.0 , 2.0 , 2.0) + transform.location
    return carla.Transform(location, transform.rotation)



def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    spectator = world.get_spectator()
    while True:
        actors_list = world.get_actors().filter('vehicle.*')
        time.sleep(1)
        print(actors_list)
        for actor in actors_list:
            transform = actor.get_transform()
            print(actor.id)
            time.sleep(3)
            spectator.set_transform(get_transform(transform))


if __name__ == '__main__':

    main()