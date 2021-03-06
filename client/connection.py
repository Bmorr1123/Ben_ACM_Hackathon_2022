import json
import threading
import socket, os


class Connection:
    LOCALHOST = socket.gethostbyname(socket.gethostname())

    def __init__(self, ip, port, name):
        super().__init__()

        self.connection = socket.socket()

        self.ip = ip
        self.port = port
        try:
            self.connection.connect((self.ip, self.port))
        except (ConnectionRefusedError, socket.gaierror):
            self.name = None
            return
        # print(f"SENT {name} to server")
        self.send(name)

        self.name = name
        self.string = ""

        self.uuid = self.receive()

        print("Getting colors")
        try:
            with open("client/res/colors.json") as file:
                data = json.load(file)
                self.send(" ".join([f"{i[0]} {i[1]} {i[2]}" for i in data]))
        except FileNotFoundError:
            self.send("200 200 200")

        self.connection.settimeout(0.01)

    def send(self, message):
        self.connection.send(f"{message}\n".encode())

    def receive(self):
        if self.string:  # If there is already data queued, return that.
            data, self.string = self.string.split("\n", 1)
            return data
        try:
            data = self.connection.recv(2048).decode()
            if "\n" in data:
                data = data.split("\n", 1)
                self.string += data[1]
                return data[0].replace("\n", "")
            return data
        except socket.timeout:
            return ""
