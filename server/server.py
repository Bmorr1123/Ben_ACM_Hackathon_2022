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
        for connection2, snake in self.connections:
            if snake:
                string = f"#snake {connection2.uuid} {connection2.name} {snake.direction} {snake.length} {len(connection2.colors)} "
                string += " ".join([f"{c[0]} {c[1]} {c[2]}" for c in connection2.colors])
                string += " " + " ".join([f"{pos[0]} {pos[1]}" for pos in snake.body])
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

        # This handles dead connections
        i = 0
        while i < len(self.connections):
            if not self.connections[i][0].alive:
                self.connections.pop(i)
            else:
                i += 1

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
                        snake.length += 1
                        self.send_all_client(f"#apple {snake.uuid} {head[0]} {head[1]}")
                        self.apples.remove(head)

                    elif collision_obj == "body":
                        self.connections[i][1] = None
                        self.send_all_client(f"#death {snake.uuid}")
                        for j, pos in enumerate(snake.body):
                            if j % 2:
                                self.create_apple(pos)

                    snake.body.append(head)
                    while len(snake.body) > snake.length:
                        snake.body.pop(0)

            self.send_all_client("tick")

    def create_snake(self, connection):
        pos = self.get_spread_pos()
        direction = randint(0, 3)
        snake = ss.Snake(connection.uuid, pos, direction)

        string = f"#snake {connection.uuid} {connection.name} {snake.direction} {snake.length} {len(connection.colors)} "
        string += " ".join([f"{c[0]} {c[1]} {c[2]}" for c in connection.colors])
        string += " " + " ".join([f"{pos[0]} {pos[1]}" for pos in snake.body])

        # print(f"Sending {string}")

        self.send_all_client(string)
        return snake

    def create_apple(self, pos):
        self.send_all_client(f"#new_apple {pos[0]} {pos[1]}")
        self.apples.append(pos)

    def send_all_client(self, message):
        # print(f"->ALL: {message}")
        for connection, snake in self.connections:
            connection.send(message)

    def get_spread_pos(self):
        pos = self.get_empty_pos()
        dist = 100
        while dist < 25:
            pos = self.get_empty_pos()
            dist = min([((snake.get_head()[0] - pos[0]) ** 2 + (snake.get_head()[1] - pos[1]) ** 2) ** (1 / 2) for
                        connection, snake in self.connections])
        return pos

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


class MultiServer(threading.Thread):
    def __init__(self, ip, port, game_server):
        super().__init__()
        self.ip, self.port = ip, port
        self.game_server = game_server

    def run(self):
        server = socket.socket()
        ip, port = self.ip, self.port

        server.bind((ip, port))
        server.listen(69420)

        print("Listening on port", port)
        print("Listening on ip", ip)

        while True:
            client, address = server.accept()
            con = sc.Connection(client)
            print("New user called", con.getNames()[0])
            self.game_server.add_connection(con)

class ConnectionServer(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        if platform == "linux" or platform == "linux2":
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        port = 3369

        game_server = GameServer()
        game_server.start()

        hostnames = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]
        for hostname in hostnames:
            try:
                ip = socket.gethostbyname(hostname)
                ms = MultiServer(ip, port, game_server)
                ms.start()
            except socket.gaierror:
                pass


def main():
    server = ConnectionServer()
    server.run()


if __name__ == '__main__':
    main()
