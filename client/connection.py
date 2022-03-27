import json
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
        print(f"SENT {name} to server")
        self.send(name)

        self.name = name
        self.string = ""

        self.uuid = self.receive()

        with open("res/colors.json") as file:
            data = json.load(file)
            self.send(" ".join([f"{i[0]} {i[1]} {i[2]}" for i in data]))

        self.connection.settimeout(0.01)

    def send(self, message):
        self.connection.send(f"{message}\n".encode())

    def receive(self):
        if self.string:  # If there is already data queued, return that.
            data, self.string = self.string.split("\n", 1)
            return data
        try:
            data = ""
            while "\n" not in data:
                data += self.connection.recv(2048).decode()

            print(f"Server -> Client: {data}")

            if "\n" in data:
                data = data.split("\n", 1)
                self.string += data[1]
                return data[0].replace("\n", "")
            return data
        except socket.timeout:
            return ""
