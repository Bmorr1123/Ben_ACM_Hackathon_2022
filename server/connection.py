import socket
from random import randint


class Connection:
    uuids = []

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.name = ""
        self.uuid = ""
        self.string = ""

        data: str = self.client.recv(1024).decode()
        self.setName(data.strip())
        color = [randint(0, 255) for i in range(3)]
        while sum(color) / 3 < 100:
            color = [randint(0, 255) for i in range(3)]

        self.send(" ".join([str(i) for i in color]))

        self.client.settimeout(0.01)

    def setName(self, name):
        self.name = name
        i = 0
        while (uuid := f"{name}{i}") in Connection.uuids:
            i += 1

        self.uuid = uuid
        Connection.uuids.append(self.uuid)
        self.send(self.uuid)

    def getNames(self):
        return self.name, self.uuid

    def send(self, message):
        self.client.send(f"{message}\n".encode())

    def receive(self):
        if self.string:  # If there is already data queued, return that.
            data, self.string = self.string.split("\n", 1)
            return data

        try:
            data = self.client.recv(1024).decode()
            if "\n" in data:
                data = data.split("\n", 1)
                self.string += data[1]
                return data[0].replace("\n", "")

            return data
        except socket.timeout:
            return ""

