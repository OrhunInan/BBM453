
import socket
import threading
import sys

# macros
MAIN_SERVER_IP = sys.argv[1]
MAIN_SERVER_PORT = int(sys.argv[2])
REPOSITORY_PATH = sys.argv[3]
SCHEDULE = sys.argv[4]


def log(str=None):
    """
    Log function is defined at the pdf, I'm just lazy AF 
    """
    print("We need to define log function")
    if str != None:
        print(str)

##TODO basically every line beloww this comment is useless, however code below will stay as an example usage of threads and sockets until we implement them.

# --- SERVER LOGIC (runs in a separate thread) ---
# This function will run in a separate thread to handle incoming messages.
def receive_messages(server_socket):
    """
    Listens for incoming connections and prints messages from other peers.
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

def start_reciever_thread(target, server_socket):
    """
    Start the server thread
    he server thread will handle incoming messages in the background.
    'daemon=True' ensures the thread will close when the main program exits.
    """
    log("You can now send messages to other peers.")    

def send_message(dest_ip, dest_port, message_to_send):
    # Create a *new* socket to send the message (acting as a client)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the destination peer
    client_socket.connect((dest_ip, dest_port))
    
    # Send the message
    client_socket.send(message_to_send.encode())
    
    # Close the connection for this message
    client_socket.close()
    log("Message sent! ✔️")


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