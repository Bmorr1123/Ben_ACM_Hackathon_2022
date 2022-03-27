class Snake:
    def __init__(self, uuid, pos, direction):
        self.uuid = uuid
        self.body = [pos]
        self.direction = direction
        self.length = 3

    def tick(self):
        head = self.body[-1]

        x, y = 0, 0
        if self.direction == 0:
            x += 1
        # Left
        elif self.direction == 1:
            x -= 1
        # Up
        elif self.direction == 2:
            y -= 1
        # Down
        elif self.direction == 3:
            y += 1

        self.body.append((head[0] + x, head[1] + y))
        if len(self.body) > self.length:
            self.body.pop(0)


