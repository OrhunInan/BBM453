import socket
import threading
import sys

SERVER_PORT = int(sys.argv[1])

peer_list = {}


def parse_message(socket, addr, input_string):

    arguments = input_string.split()

    # Since every argument starts with start we look at the second word
    match arguments[1]:
        case "SERVING":
            peer_list[f"{addr[0]}:{arguments[2]}"] = [] # empty list will be filled with available files after
        
        case "PROVIDING":
            peer_port = f"{addr[0]}:{arguments[2]}"
            serve_list = [arguments[4 + i] for i in range(int(arguments[3]))]

            peer_list[peer_port] = serve_list


        case "SEARCH":
                
                print(peer_list)
        
                result = [port for port, file_list in peer_list.items() if arguments[2] in file_list]

                try:
                    print(f"\n\n{result}\n\n")

                    print("sending")
                    print(socket.send(f"START PROVIDERS {" ".join(result if len(result) <= 2 else result)} END".encode()))
                    socket.send(f"START PROVIDERS {" ".join(result if len(result) <= 2 else result)} END".encode())
                except Exception as e:
                    print(f"Error sending search result: {e}")



server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', SERVER_PORT))
print(f"address: {server_socket.getsockname()[0]}\nport: {server_socket.getsockname()[1]}")

while True:
    server_socket.listen()
    # Wait for a connection from another client
    connection_socket, addr = server_socket.accept()
    # Receive the message from the peer
    message = connection_socket.recv(1024).decode()
    if message: 
        for line in message.split("END"): 
            if len(line) != 0:
                parse_message(connection_socket, addr, line)
    connection_socket.close()
