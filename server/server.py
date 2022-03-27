import socket
from connection import Connection
import threading
from snake import Snake
from random import randint
import time


class GameServer(threading.Thread):
    time_step = 1 / 5

    def __init__(self):
        super().__init__()

        self.connections = []
        self.apples = []
        self.time = time.time()

        self.game_time = 0

    def add_connection(self, connection):
        self.connections.append([connection, None])

    def run(self):
        self.time = time.time()
        while True:
            ct = time.time()
            self.tick(ct - self.time)
            self.time = ct
            time.sleep(0.001)

    def tick(self, delta):
        self.game_time += delta
        do_tick = self.game_time > GameServer.time_step
        if do_tick:
            self.game_time -= GameServer.time_step

        for i, (connection, snake) in enumerate(self.connections):

            # Connection Handling
            info: str = connection.receive()
            if info.startswith("#") and snake:  # Does # only if client has a snake
                args = info[1:].split(" ")

                if args[1] == "turn":
                    snake.direction = int(args[2])
                    self.send_all_client(f"#turn {snake.uuid} {snake.direction}")

            elif info == "join":
                self.connections[i][1] = self.create_snake(connection)

            # Game Handling
            if do_tick:
                snake.tick()
                head = snake.get_head()
                collision_obj = self.get_pos(head)

                if collision_obj == "apple":
                    self.send_all_client(f"#apple {snake.uuid} {head[0]} {head[1]}")
                    self.apples.remove(head)

                elif collision_obj == "body":
                    self.send_all_client(f"#death {snake.uuid}")
                    for pos in snake.body:
                        if not randint(0, 3):
                            self.create_apple(pos)

    def create_snake(self, connection):
        pos = self.get_empty_pos()
        direction = randint(0, 3)
        self.send_all_client(f"#snake {connection.uuid} {connection.name} {pos[0]} {pos[1]} {direction}")
        return Snake(connection.uuid, pos, direction)

    def create_apple(self, pos):
        self.send_all_client(f"#new_apple {pos[0]} {pos[1]}")
        self.apples.append(pos)

    def send_all_client(self, message):
        for connection, snake in self.connections:
            connection.send(message)

    def get_empty_pos(self):
        while self.get_pos(pos := (randint(0, 99), randint(0, 99))):
            pass
        return pos

    def get_pos(self, pos: tuple):
        if pos in self.apples:
            return "apple"

        for connection, snake in self.connections:
            if pos in snake.body:
                return "body"

        if not (0 <= pos[0] < 100 and 0 <= pos[1] < 100):
            return "body"

        return None


class ConnectionServer(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        port = 3369
        running = True

        game_server = GameServer()
        game_server.start()

        server = socket.socket()
        server.bind(("localhost", port))
        server.listen(69420)

        while running:
            client, address = server.accept()
            con = Connection(client)
            con.getName()
            print("New user called", con.getNames()[0])
            game_server.connections.append(con)
            con.send(" ".join([str(randint(100, 255)) for i in range(3)]))

        print("Listening on port", port)


def main():
    server = ConnectionServer()
    server.run()


if __name__ == '__main__':
    main()
