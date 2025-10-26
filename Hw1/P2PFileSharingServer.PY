import socket
import threading
import sys

peer_list = {}


def parse_message(input_string):

    arguments = input_string.split()

    # Since every argument starts with start we look at the second word
    match input_string[1]:
        case "SERVING":
            peer_list[int(input_string[2])] = [] # empty list will be filled with available files after
        
        case "PROVIDING":
            peer_port = int(input_string[2])
            serve_list = [input_string[3 + i] for i in int(input_string[3])]

            peer_list[peer_port] = serve_list

    """
    while True:
        try:
            # Wait for a connection from another peer
            connection_socket, addr = server_socket.accept()
            # Receive the message from the peer
            message = connection_socket.recv(1024).decode()
            if message:
                log(message)
            connection_socket.close()
        except Exception as e:
            log(f"Error receiving message: {e}")
            break
            """
