import socket
import numpy as np
import _thread

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ("localhost", 10000)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(5)


def open_file(name):
    file = open(name, "r")
    content = file.readlines()
    instructions = []
    size = 0
    # Get amount of nodes
    # Save distance and traffic into instructions array
    for i in content:
        if "," not in i:
            size += 1
        else:
            instructions.append(i)
    # Creation of adjacency adj_matrix
    adj_matrix = np.ones((size, size, 2)) * 999

    # Diagonal of 0s
    for i in range(len(adj_matrix)):
        for j in range((len(adj_matrix))):
            if i == j:
                adj_matrix[i][j] = 0

    # Add distance and traffic to the adjacency matrix
    for i in instructions:
        parts = i.split(",")
        pos1 = int(parts[0].replace("n", ""))
        pos2 = int(parts[1].replace("n", ""))
        dist = int(parts[2])
        level = parts[3].strip()

        if level == "light":
            adj_matrix[pos1][pos2], adj_matrix[pos1][pos2][1] = dist, 100
        elif level == "medium":
            adj_matrix[pos1][pos2], adj_matrix[pos1][pos2][1] = dist, 50
        elif level == "heavy":
            adj_matrix[pos1][pos2], adj_matrix[pos1][pos2][1] = dist, 20

    return adj_matrix


def shortest_path(matrix):
    size = len(matrix[0])
    path_matrix = np.zeros([size, size])
    for k in range(size):
        for j in range(size):
            for i in range(size):
                # Distance
                p1 = matrix[i][k][0]
                p2 = matrix[k][j][0]
                p3 = matrix[i][j][0]
                # Velocity
                v1 = matrix[i][k][1]
                v2 = matrix[k][j][1]
                v3 = matrix[i][j][1]
                if v1 == 0 or v2 == 0 or v3 == 0:
                    continue
                # Time
                t1 = p1 / v1
                t2 = p2 / v2
                t3 = p3 / v3
                # Checks if it's better to pass by an intermediate node or not
                if t1 + t2 < t3:
                    matrix[i][j][0] = p1 + p2
                    path_matrix[i][j] = k
    return path_matrix


def process(nodes, matrix, short_paths):
    start = int(nodes[0])
    end = int(nodes[1])
    path = []
    if matrix[start][end][0] != 999:
        # Path rebuilding
        while end != 0:
            path.append(end)
            end = int(short_paths[start][end])
        path.append(start)
        return list(reversed(path))

    else:
        return "n"


print("Hello! \nType the file's name to load data: ")
name = input()
matrix = open_file(name)
sh_m = shortest_path(matrix)


def accept_client(connection, client_address):
    while True:
        try:
            print('Connection from', client_address)

            # Receive the data
            while True:
                data = connection.recv(16)
                # Turning received data into String
                info = data.decode("utf-8")
                info = info.split(",")
                finalResp = ', '.join(map(str, process(info, matrix, sh_m)))

                if data:
                    data = bytes(finalResp, "utf-8")
                    connection.sendall(data)
                else:
                    print("no data from", client_address)
                    break

        finally:
            # Clean up the connection
            connection.close()


while True:
    # Wait for a connection
    print("Waiting for a connection")
    connection, client_address = sock.accept()
    _thread.start_new_thread(accept_client, (connection, client_address))



