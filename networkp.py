import socket
import pickle
import numpy as np


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initiates socket ipv4 TCP
        self.server = "192.168.1.103"  # ip address of server
        self.port = 5555  # port to use - 5555 is often open and unused
        self.addr = (self.server, self.port)
        self.c = self.connect()


    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048*4)) # returns connected
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048*6))
        except socket.error as e:
            print(e)
