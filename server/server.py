import socket


def main():
    port = 3369
    running = True

    server = socket.socket()
    server.bind(("localhost", port))
    server.listen(4)

    while running:
        client, address = server.accept()
        print("New connection from:", address)
        data = client.recv(1024)
        print(f"Client: {data.decode()}")
        client.send("Welcome to the server!".encode())

    print("Listening on port", port)


if __name__ == '__main__':
    main()