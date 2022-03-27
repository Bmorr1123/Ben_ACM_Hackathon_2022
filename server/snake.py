class Snake:
    def __init__(self, uuid, pos, direction):
        self.uuid = uuid
        self.body = [pos]
        self.direction = direction
        self.length = 6

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

        # print(x, y)
        new_head = head[0] + x, head[1] + y
        # print(f"\nServer: {self.ticks} {new_head}")
        self.ticks += 1
        return new_head


