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
        print(f"RECV {data}")
        self.setName(data.strip())

        rec = self.receive()
        print(rec)
        colors = [int(i) for i in rec.split(" ")]
        print(colors)
        self.colors = [colors[i:i + 3] for i in range(0, int(len(colors)), 3)]
        print(self.colors)

        self.client.settimeout(0.005)
        self.alive = True

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
        print(f"Server -> Client: {message}")
        self.client.send(f"{message}\n".encode())

    def receive(self):
        if self.string:  # If there is already data queued, return that.
            data, self.string = self.string.split("\n", 1)
            return data

        try:
            data = ""
            while "\n" not in data:
                data += self.client.recv(2048).decode()

            if "\n" in data:
                data = data.split("\n", 1)
                self.string += data[1]
                return data[0].replace("\n", "")

            return data
        except socket.timeout:
            return ""
        except (ConnectionAbortedError, ConnectionResetError):
            self.alive = False
            return ""

