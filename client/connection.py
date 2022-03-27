import threading
import socket


class Connection:
    LOCALHOST = socket.gethostbyname(socket.gethostname())

    def __init__(self, ip, port, name):
        super().__init__()

        self.connection = socket.socket()

        self.ip = ip
        self.port = port

        self.connection.connect((self.ip, self.port))
        self.send(name)

        self.name = name
        self.string = ""

        self.uuid = self.receive()
        self.color = [int(i) for i in self.receive().split(" ")]
        self.connection.settimeout(0.01)

    def send(self, message):
        self.connection.send(f"{message}\n".encode())

    def receive(self):
        if self.string:  # If there is already data queued, return that.
            data, self.string = self.string.split("\n", 1)
            return data
        try:
            data = self.connection.recv(1024).decode()
            if "\n" in data:
                data = data.split("\n", 1)
                self.string += data[1]
                return data[0].replace("\n", "")

            return data
        except socket.timeout:
            return ""
