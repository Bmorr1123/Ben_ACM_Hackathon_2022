import threading
import socket


class Connection():

    def __init__(self, ip, port):
        self.connection = None
        self.ip = ip
        self.port = port
        super().__init__()

    def connect(self):
        self.connection = socket.socket()
        self.connection.connect((self.ip, self.port))

    def send(self, message):
        self.connection.send(message.encode())

    def recieve(self):
        data = self.connection.recv(1024).decode()
        return data
