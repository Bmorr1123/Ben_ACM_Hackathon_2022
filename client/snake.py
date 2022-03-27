class Snake:
    def __init__(self, uuid, name, pos, direction):
        self.uuid = uuid
        self.name = name

        self.body = [pos]
        self.direction = direction
        self.length = 6

        self.colors = [[100, 100, 100]]

        self.ticks = 0

    def get_head(self):
        return self.body[-1]

    def tick(self):
        head = self.get_head()

        x, y = 0, 0
        if self.direction == 0:
            x -= 1
        elif self.direction == 1:
            y += 1
        elif self.direction == 2:
            x += 1
        elif self.direction == 3:
            y -= 1

        # print(f"Client: {self.ticks} {(head[0] + x, head[1] + y)}")

        self.body.append((head[0] + x, head[1] + y))
        if len(self.body) > self.length:
            self.body.pop(0)

        self.ticks += 1
