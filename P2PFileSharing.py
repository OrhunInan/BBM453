# p2p_chat.py
import socket
import threading

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
                # Print the message with the sender's address
                print(f"\n[Message from {addr[0]}:{addr[1]}]: {message}")
                print("Enter destination IP: ", end="") # Re-prompt user
            connection_socket.close()
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# --- CLIENT LOGIC (runs in the main thread) ---
def main():
    """
    Main function to set up the peer and handle sending messages.
    """
    # 1. Set up the server part of the peer
    # Use '0.0.0.0' to listen on all available network interfaces
    host = '0.0.0.0'
    # Ask the user to choose a port for their peer to listen on
    port = int(input("Enter the port for this peer to listen on: "))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5) # Listen for up to 5 incoming connections
    print(f"✅ Peer is running and listening on {host}:{port}")

    # 2. Start the server thread
    # The server thread will handle incoming messages in the background.
    # 'daemon=True' ensures the thread will close when the main program exits.
    receiver_thread = threading.Thread(target=receive_messages, args=(server_socket,), daemon=True)
    receiver_thread.start()
    print("You can now send messages to other peers.")

    # 3. Handle sending messages in a loop
    while True:
        try:
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
            print("Message sent! ✔️")

        except ConnectionRefusedError:
            print("❌ Connection refused. Make sure the destination peer is running and the IP/port are correct.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()