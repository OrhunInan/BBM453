import socket
import threading
import sys

peer_list = {}


def parse_message(soccket, addr, input_string):

    arguments = input_string.split()

    # Since every argument starts with start we look at the second word
    match input_string[1]:
        case "SERVING":
            peer_list[f"{addr}:{input_string[2]}"] = [] # empty list will be filled with available files after
            return None
        
        case "PROVIDING":
            peer_port = f"{addr}:{input_string[2]}"
            serve_list = [input_string[3 + i] for i in int(input_string[3])]

            peer_list[peer_port] = serve_list

            return None

        case "SEARCH":
                result = [
                port for port, file_list in peer_list.items() 
                if input_string[2] in file_list
                ]

                try:
                    soccket.send(f"START PROVIDERS {" ".join(result)} END".encode())
                except Exception as e:
                    print(f"Error sending search result: {e}")



    
    while True:
        try:
            # Wait for a connection from another client
            connection_socket, addr = server_socket.accept()
            # Receive the message from the peer
            message = connection_socket.recv(1024).decode()
            if message:
                parse_message(connection_socket, addr, message)
            connection_socket.close()
        except Exception as e:
            log(f"Error receiving message: {e}")
