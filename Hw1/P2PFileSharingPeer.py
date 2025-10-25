"""
sys.argv[1] = ip
sys.argv[2] = port
"""


# p2p_chat.py
import socket
import threading
import sys

def append_log(str=None):
    """
    Log function is defined at the pdf, I'm just lazy AF 
    """
    print("We need to define log function")
    if str != None:
        print(str)

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
                append_log(message)
            connection_socket.close()
        except Exception as e:
            append_log(f"Error receiving message: {e}")
            break

def start_server():
    """
    Set up the server part of the peer
    Use '0.0.0.0' to listen on all available network interfaces
    """
    host = sys.argv[1]
    port = int(sys.argv[2])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5) # Listen for up to 5 incoming connections

    return server_socket

def start_reciever_thread(target, server_socket):
    """
    Start the server thread
    he server thread will handle incoming messages in the background.
    'daemon=True' ensures the thread will close when the main program exits.
    """

    receiver_thread = threading.Thread(target=target, args=(server_socket,), daemon=True)
    receiver_thread.start()
    append_log("You can now send messages to other peers.")    

def send_message():
    # Get the destination peer's information from the user
    dest_ip = input("Enter destination IP (e.g., 127.0.0.1): ")
    dest_port = int(input("Enter destination port: "))
    message_to_send = input("Enter your message: ")

    # Create a *new* socket to send the message (acting as a client)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the destination peer
    client_socket.connect((dest_ip, dest_port))
    
    # Send the message
    client_socket.send(message_to_send.encode())
    
    # Close the connection for this message
    client_socket.close()
    append_log("Message sent! ✔️")

server_socket = start_server()
start_reciever_thread(receive_messages, server_socket)

# 3. Handle sending messages in a loop
while True:
    try:
        send_message()
    except ConnectionRefusedError:
        append_log("❌ Connection refused. Make sure the destination peer is running and the IP/port are correct.")
    except Exception as e:
        append_log(f"An error occurred: {e}")