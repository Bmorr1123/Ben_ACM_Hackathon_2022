import socket
from connection import Connection
import threading
from snake import Snake
from random import randint
import time

class GameServer(threading.Thread):

    time_step = 1/5

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

            if info.startswith("#"):
                args = info[1:].split(" ")
                if args[0] == "join":

                    while self.get_pos(pos := (randint(0, 99), randint(0, 99))):
                        pass
                    self.connections[i][1] = Snake(connection.uuid, pos, randint(0, 3))
                if args[0] == "snake" and snake:  # Does this only if they have an alive Snake
                    if args[1] == "turn":
                        snake.direction = int(args[2])

            # Game Handling
            if do_tick:
                snake.tick()
                head = snake.get_head()
                collision_obj = self.get_pos(head)
                if collision_obj == "apple":
                    self.send_all_client(f"#apple {snake.uuid}")
                elif collision_obj == "body":
                    self.send_all_client(f"#die {snake.uuid}")

    def send_all_client(self, message):
        for connection, snake in self.connections:
            connection.send(message)

    def get_pos(self, pos: tuple):
        if pos in self.apples:
            return "apple"

        for connection, snake in self.connections:
            if pos in snake.body:
                return "body"

        if not (0 <= pos[0] < 100 and 0 <= pos[1] < 100):
            return "body"

        return None

def main():
    port = 3369
    running = True

    game_server = GameServer()

    server = socket.socket()
    server.bind(("localhost", port))
    server.listen(4)

    while running:
        client, address = server.accept()
        con = Connection(client)
        con.getName()
        print("New user called", con.getNames()[0])
        game_server.connections.append(con)

    print("Listening on port", port)


if __name__ == '__main__':
    main()
