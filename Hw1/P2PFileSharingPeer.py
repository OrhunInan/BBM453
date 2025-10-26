
import socket
import threading
import sys

# macros
MAIN_SERVER_IP = sys.argv[1]
MAIN_SERVER_PORT = int(sys.argv[2])
REPOSITORY_PATH = sys.argv[3]
SCHEDULE = sys.argv[4]


"""
Log function is defined at the pdf, I'm just lazy AF 
"""
def log(str=None):
    print("We need to define log function")
    if str != None:
        print(str)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind(("", 0))

client_port = client_socket.getsockname()[1]

client_socket.connect((MAIN_SERVER_IP, MAIN_SERVER_PORT))


print(f"START SERVING {client_port} END")
client_socket.send(f"START SERVING {client_port} END".encode())
print(f"START PROVIDING {client_port} 1 a.dat END")
client_socket.send(f"START PROVIDING {client_port} 1 a.dat END".encode())
print(f"START SEARCH a.dat END")
client_socket.send(f"START SEARCH a.dat END".encode())
print(client_socket.recv(10240).decode())
client_socket.close()