class Connection:
    uuids = []

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.name = ""
        self.uuid = ""

    def setName(self, name):
        self.name = name
        uuid = name
        if name in Connection.uuids:
            new_name = name + "1"
            self.setName(name, new_name)
            pass
        else:
            self.uuid = uuid
            Connection.uuids.append(self.uuid)

    def getNames(self):
        return self.name, self.uuid

    def getName(self):
        data: str = self.client.recv(1024).decode()
        self.setName(data.strip())
        return self.name

    def send(self, message):
        self.client.send(message.encode())

    def receive(self):
        # TODO: Check if we need to .split("\n")
        return self.client.recv(1024).decode()
