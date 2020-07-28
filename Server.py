import _thread
import socket
import numpy as np


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ("localhost", 10000)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(5)


# This method opens the file received by input and constructs the adjacency matrix
def open_file(file):
    file = open(file, "r")
    content = file.readlines()
    instructions = []
    size = 0
    for i in content:
        # Get amount of nodes
        if "," not in i:
            size += 1
        # Save distance and traffic into instructions array
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

        # light = 100 km/h, medium = 50 km/h, heavy = 20 km/h
        if level == "light":
            adj_matrix[pos1][pos2], adj_matrix[pos1][pos2][1] = dist, 100
        elif level == "medium":
            adj_matrix[pos1][pos2], adj_matrix[pos1][pos2][1] = dist, 50
        elif level == "heavy":
            adj_matrix[pos1][pos2], adj_matrix[pos1][pos2][1] = dist, 20

    return adj_matrix


# This method builds the matrix that contains the best path between nodes
def shortest_path(p_matrix):
    size = len(p_matrix[0])
    path_matrix = np.zeros([size, size])
    for k in range(size):
        for j in range(size):
            for i in range(size):
                # Distance
                p1 = p_matrix[i][k][0]
                p2 = p_matrix[k][j][0]
                p3 = p_matrix[i][j][0]
                # Velocity
                v1 = p_matrix[i][k][1]
                v2 = p_matrix[k][j][1]
                v3 = p_matrix[i][j][1]
                # Avoid division by 0
                if v1 == 0 or v2 == 0 or v3 == 0:
                    continue
                # Time
                t1 = p1 / v1
                t2 = p2 / v2
                t3 = p3 / v3
                # Checks if it's better to pass by an intermediate node or not
                if t1 + t2 < t3:
                    p_matrix[i][j][0] = p1 + p2
                    path_matrix[i][j] = k
    return path_matrix


# This method is the one that rebuilds the path
def process(nodes, p_matrix, short_paths):
    start = int(nodes[0])
    end = int(nodes[1])
    path = []
    if p_matrix[start][end][0] != 999:
        # Path rebuilding
        while end != 0:
            path.append(end)
            end = int(short_paths[start][end])
        path.append(start)
        return list(reversed(path))
    else:
        return "n"


print("Hello! \nType the file's name to load the data: ")
name = input()
# Creation of the adjacency matrix
matrix = open_file(name)
# Creation of the shortest paths matrix
short_matrix = shortest_path(matrix)
# Saves both matrices into a single file in compressed .npz format.
np.savez_compressed('outfile', matrix=matrix, sh_m=short_matrix)


def accept_client(p_connection, p_client_address):
    while True:
        try:
            print('Connection from', p_client_address)

            # Receive the data
            while True:
                data = p_connection.recv(16)
                # Turning received data into String
                info = data.decode("utf-8")
                info = info.split(",")
                finalResp = " ,".join(map(str, process(info, matrix, short_matrix)))

                if data:
                    data = bytes(finalResp, "utf-8")
                    p_connection.sendall(data)
                else:
                    print("No data from", p_client_address)
                    break

        finally:
            # Clean up the connection
            p_connection.close()


while True:
    # Wait for a connection
    print("Waiting for a connection")
    connection, client_address = sock.accept()
    _thread.start_new_thread(accept_client, (connection, client_address))
