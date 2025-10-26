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
                result = [port for port, file_list in peer_list.items() if arguments[2] in file_list]

                try:
                    socket.send(f"START PROVIDERS {" ".join(result if len(result) <= 2 else result)} END".encode())
                except Exception as e:
                    print(f"Error sending search result: {e}")

def client_thread(connection_socket, addr):
    try:
        # Receive the message from the peer
        while True:
            message = connection_socket.recv(1024).decode()
            if message: 
                for line in message.split("END"): 
                    if len(line) != 0:
                        parse_message(connection_socket, addr, line)
            else:
                connection_socket.close()
    except Exception as e:
        connection_socket.close()





server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', SERVER_PORT))

while True:
    server_socket.listen()
    # Wait for a connection from another client
    connection_socket, addr = server_socket.accept()

    #create thread for client
    new_thread = threading.Thread(target=client_thread, args=(connection_socket, addr), daemon=True)
    new_thread.start()


