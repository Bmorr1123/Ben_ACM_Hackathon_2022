import socket


def main():

    name = input("Input name: ")

    port = 3369
    running = True

    connection = socket.socket()
    connection.connect(("localhost", port))

    connection.send(name.encode())
    print(connection.recv(1024).decode())

if __name__ == '__main__':
    main()
