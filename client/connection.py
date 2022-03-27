import threading
import socket

class Connection(threading.Thread):
    uuids = []

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.name = ""
        self.uuid = ""

    def connect(self, ip, port):
        self.connection = socket.socket()
        self.connection.connect(ip, port)


    def send(self, message):
        self.client.send(message.encode())

    def recieve(self):
        data = self.client.recv(1024).decode()
        return data
