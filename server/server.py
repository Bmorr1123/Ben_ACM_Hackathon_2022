import socket
try:
    import server.connection as sc
    import server.snake as ss
except ModuleNotFoundError:
    import connection as sc
    import snake as ss
import threading
import signal
from sys import platform
from random import randint
import time


class GameServer(threading.Thread):
    time_step = 1/10

    def __init__(self):
        super().__init__()

        self.connections = []
        self.apples = []
        self.time = time.time()

        self.game_time = 0

    def add_connection(self, connection):
        self.connections.append([connection, None])
        for pos in self.apples:
            connection.send(f"#new_apple {pos[0]} {pos[1]}")
        for connection, snake in self.connections:
            if snake:
                string = f"#snake {connection.uuid} {connection.name} {snake.direction} "
                string += " ".join([f"{pos[0]} {pos[1]}" for pos in snake.body])
                connection.send(string)

    def run(self):
        self.time = time.time()
        while True:
            ct = time.time()
            self.tick(ct - self.time)
            self.time = ct
            time.sleep(0.001)

    def tick(self, delta):
        self.game_time += delta

        for i, (connection, snake) in enumerate(self.connections):

            # Connection Handling
            while info := connection.receive():
                if info[0] and snake:  # Does # only if client has a snake
                    args = info[1:].split(" ")

                    if args[0] == "turn":
                        snake.direction = int(args[1])
                        self.send_all_client(f"#turn {snake.uuid} {snake.direction}")

                elif info == "join":
                    self.connections[i][1] = self.create_snake(connection)

        do_tick = self.game_time > GameServer.time_step
        if do_tick:
            self.game_time -= GameServer.time_step
            while len(self.apples) < len(self.connections) * 3:
                self.create_apple(self.get_empty_pos())

            for i, (connection, snake) in enumerate(self.connections):
                # Game Handling
                if snake:
                    head = snake.tick()
                    collision_obj = self.get_pos(head)

                    if collision_obj == "apple":
                        self.send_all_client(f"#apple {snake.uuid} {head[0]} {head[1]}")
                        self.apples.remove(head)

                    elif collision_obj == "body":
                        self.connections[i][1] = None
                        self.send_all_client(f"#death {snake.uuid}")
                        for pos in snake.body:
                            if not randint(0, 3):
                                self.create_apple(pos)

                    snake.body.append(head)
                    while len(snake.body) > snake.length:
                        snake.body.pop(0)

            self.send_all_client("tick")

    def create_snake(self, connection):
        pos = self.get_empty_pos()
        direction = randint(0, 3)
        self.send_all_client(f"#snake {connection.uuid} {connection.name} {direction} {pos[0]} {pos[1]}")
        return ss.Snake(connection.uuid, pos, direction)

    def create_apple(self, pos):
        self.send_all_client(f"#new_apple {pos[0]} {pos[1]}")
        self.apples.append(pos)

    def send_all_client(self, message):
        print(message)
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
            if snake:
                if pos in snake.body:
                    return "body"

        if not (0 <= pos[0] < 100 and 0 <= pos[1] < 100):
            return "body"

        return None


class ConnectionServer(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        if platform == "linux" or platform == "linux2":
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        port = 3369
        running = True

        game_server = GameServer()
        game_server.start()

        server = socket.socket()
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        server.bind((ip, port))
        server.listen(69420)

        print("Listening on port", port)
        print("Listening on ip", ip)

        while running:
            client, address = server.accept()
            con = sc.Connection(client)
            print("New user called", con.getNames()[0])
            game_server.add_connection(con)


def main():
    server = ConnectionServer()
    server.run()


if __name__ == '__main__':
    main()
