from threading import Thread
from time import sleep

import socket
import pickle
from .worldmap import *
class ListenerThread(Thread):
    def __init__(self, worldmap, port=1800, perched=None):
        super().__init__()
        self.port = port
        self.socket = None
        self.started = False
        self.foreign_objects = {}
        self.perched = perched
        self.world_map = worldmap
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(True)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True) #enables server restart
        self.socket.bind(("", self.port))
        self.threads = []
        for i in range(50):
            self.socket.listen(5)
            c, addr = self.socket.accept()
            print("Got Connection From: ",addr)
            self.threads.append(ClientHandlerThread(i, c, self.perched, self.world_map))
            self.threads[i].start()

class ClientHandlerThread(Thread):
    def __init__(self, thread_id, client, perched, world_map):
        super().__init__()
        self.threadID = thread_id
        self.c = client
        self.perched = perched
        self.world_map = world_map
        self.c.sendall(pickle.dumps("Hello"))
        self.aruco_id = int(pickle.loads(self.c.recv(1024)))
        self.name = "Client-"+str(self.aruco_id)
        #update camera landmark pool???
        self.to_send = {}
        print("Initialized thread for: ",self.name)

    def run(self):
        while True:
            #send from server to clients
            for key, value in self.world_map.objects.items():
                if isinstance(key,LightCube):
                    self.to_send["LightCubeForeignObj-"+str(value.id)]= LightCubeForeignObj(id=value.id, x=value.x, y=value.y, z=value.z, theta=value.theta)
                elif isinstance(key,str):
                    print(key)
                    # Send walls and cameras
                    self.to_send[key] = value         # Fix case when object removed from shared map
                else:
                    print("ELSE")
                    print(key, value)
                    pass                              # Nothing else in sent
            # append 'end' to end to mark end
            print("TOSEND: "+str([self.perched.local_cameras,self.to_send]))
            self.c.sendall(pickle.dumps([self.perched.local_cameras,self.to_send])+b'end')
            sleep(0.1)
            # hack to recieve variable size data without crashing
            data = b''
            while True:
                data += self.c.recv(1024)
                if data[-3:]==b'end':
                    break
            '''
            cams, landmarks, foreign_objects, pose = pickle.loads(data[:-3])
            for key, value in cams.items():
                if key in self.robot.world.perched.camera_pool:
                    self.world_map.perched.camera_pool[key].update(value)
                else:
                    self.robot.world.perched.camera_pool[key]=value
            self.world_map.foreign_objects[self.aruco_id] = foreign_objectsarks)
            '''
