import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ("localhost", 10000)
sock.connect(server_address)

try:
    condition = True
    while condition:
        print("What would you like to do now?: \n 1. Look for a route \n 2. Exit")
        choice = int(input())
        if choice == 2:
            print("Bye!")
            break
        elif choice == 1:
            print("Start node: ")
            start = int(input())
            print("End node: ")
            end = int(input())

            # Send data
            message = bytes(f"{start},{end}", encoding="utf8")
            sock.sendall(message)

            # Look for the response
            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                info = data.decode("utf-8")
                if info == "n":
                    print("Sorry! No path available between these nodes", "\n")
                    break
                else:
                    print("The best path between the nodes is:", info, "\n")

finally:
    print("Closing socket")
    sock.close()
