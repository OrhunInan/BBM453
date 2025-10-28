# P2PFileSharingServer.py

"""
Starts listening on a given port.
Accepts connections from peers.
Each peer runs in its own thread (client_thread).
When a message arrives, it's passed to parse_message().
"""

import socket
import threading
import sys

SERVER_PORT = int(sys.argv[1])

peer_list = {}
peer_list_lock = threading.Lock()


def parse_message(connection_socket, addr, input_string):
    arguments = input_string.strip().split()
    
    if len(arguments) < 2:
        return

    # Since every argument starts with START we look at the second word
    command = arguments[1]
    
    if command == "SERVING":
        peer_port = arguments[2]
        with peer_list_lock:
            peer_list[f"{addr[0]}:{peer_port}"] = []
        print(f"Peer {addr[0]}:{peer_port} started serving")
    
    elif command == "PROVIDING":
        peer_port = arguments[2]
        num_files = int(arguments[3])
        serve_list = [arguments[4 + i] for i in range(num_files)]

        peer_id = f"{addr[0]}:{peer_port}"
        with peer_list_lock:
            if peer_id in peer_list:
                # Add new files to existing list (avoid duplicates)
                for file in serve_list:
                    if file not in peer_list[peer_id]:
                        peer_list[peer_id].append(file)
            else:
                peer_list[peer_id] = serve_list
        
        print(f"Peer {peer_id} now provides: {peer_list[peer_id]}")

    elif command == "SEARCH":
        filename = arguments[2]
        with peer_list_lock:
            result = [port for port, file_list in peer_list.items() if filename in file_list]

        try:
            response = f"START PROVIDERS {' '.join(result)} END"
            connection_socket.send(response.encode())
            print(f"Search for {filename}: Found {len(result)} peers - {result}")
        except Exception as e:
            print(f"Error sending search result: {e}")


def client_thread(connection_socket, addr):
    print(f"New connection from {addr}")
    try:
        buffer = ""
        while True:
            data = connection_socket.recv(4096)
            if not data:
                break
            
            buffer += data.decode()
            
            # Process all complete messages (ending with END)
            while "END" in buffer:
                message, buffer = buffer.split("END", 1)
                message = message.strip()
                if len(message) > 0:
                    print(f"Received from {addr}: {message}")
                    parse_message(connection_socket, addr, message)
                    
    except Exception as e:
        print(f"Client thread error from {addr}: {e}")
    finally:
        print(f"Connection closed from {addr}")
        connection_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', SERVER_PORT))
server_socket.listen(5)

print(f"Server started on port {SERVER_PORT}")

while True:
    # Wait for a connection from another client
    connection_socket, addr = server_socket.accept()

    # Create thread for client
    new_thread = threading.Thread(target=client_thread, args=(connection_socket, addr), daemon=True)
    new_thread.start()