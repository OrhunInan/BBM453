# P2PFileSharingPeer.py

import socket
import threading
import sys
import os
import time

# Parse command line arguments
args = sys.argv[1].split(':')
MAIN_SERVER_IP = args[0]
MAIN_SERVER_PORT = int(args[1])
REPOSITORY_PATH = sys.argv[2]
SCHEDULE_FILE = sys.argv[3]

# Global variables
client_port = None
server_socket_conn = None
file_lock = threading.Lock()


def log(filename, peer_info):
    """Log download activity"""
    log_file = "peer.log"
    try:
        with open(log_file, 'a') as f:
            f.write(f"{filename} {peer_info}\n")
        f.close()
    except Exception as e:
        print(f"Error writing log: {e}")


def get_local_files():
    """Get list of files in repository"""
    try:
        files = [f for f in os.listdir(REPOSITORY_PATH) if os.path.isfile(os.path.join(REPOSITORY_PATH, f))]
        return files
    except Exception as e:
        print(f"Error reading repository: {e}")
        return []


def send_providing_message(filename):
    """Send PROVIDING message to server"""
    global server_socket_conn
    try:
        message = f"START PROVIDING {client_port} 1 {filename} END"
        server_socket_conn.send(message.encode())
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending PROVIDING message: {e}")


def search_file(filename):
    """Search for peers that have the file"""
    global server_socket_conn
    try:
        message = f"START SEARCH {filename} END"
        server_socket_conn.send(message.encode())
        print(f"Sent: {message}")
        
        # Receive response
        response = server_socket_conn.recv(10240).decode()
        print(f"Received: {response}")
        
        # Parse response: START PROVIDERS <IP:Port> ... END
        parts = response.split()
        if len(parts) > 2 and parts[0] == "START" and parts[1] == "PROVIDERS":
            providers = []
            for i in range(2, len(parts)):
                if parts[i] == "END":
                    break
                providers.append(parts[i])
            return providers
        return []
    except Exception as e:
        print(f"Error searching file: {e}")
        return []


def download_file_chunk(peer_ip, peer_port, filename, start_byte, end_byte):
    """Download a chunk of file from a peer"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer_ip, int(peer_port)))
        
        # Send download request
        request = f"START DOWNLOAD {filename} {start_byte} {end_byte} END"
        sock.send(request.encode())
        
        # Receive file data
        data = b""
        expected_size = end_byte - start_byte + 1
        while len(data) < expected_size:
            chunk = sock.recv(min(8192, expected_size - len(data)))
            if not chunk:
                break
            data += chunk
        
        sock.close()
        
        # Log the download
        log(filename, f"{peer_ip}:{peer_port}")
        
        return data
    except Exception as e:
        print(f"Error downloading chunk from {peer_ip}:{peer_port}: {e}")
        return None


def download_file_parallel(providers, filename, file_size):
    """Download file in parallel from multiple peers"""
    if not providers:
        print(f"No providers found for {filename}")
        return False
    
    num_providers = len(providers)
    chunk_size = file_size // num_providers
    
    threads = []
    chunks = [None] * num_providers
    
    def download_worker(index, provider, start, end):
        peer_ip, peer_port = provider.split(':')
        data = download_file_chunk(peer_ip, peer_port, filename, start, end)
        chunks[index] = data
    
    # Start download threads
    for i, provider in enumerate(providers):
        start_byte = i * chunk_size
        end_byte = ((i + 1) * chunk_size - 1) if i < num_providers - 1 else file_size - 1
        
        thread = threading.Thread(target=download_worker, args=(i, provider, start_byte, end_byte))
        thread.start()
        threads.append(thread)
    
    # Wait for all downloads to complete
    for thread in threads:
        thread.join()
    
    # Combine chunks
    if all(chunk is not None for chunk in chunks):
        with file_lock:
            filepath = os.path.join(REPOSITORY_PATH, filename)
            with open(filepath, 'wb') as f:
                for chunk in chunks:
                    f.write(chunk)
        print(f"Successfully downloaded {filename}")
        get_local_files()
        return True
    else:
        print(f"Failed to download {filename}")
        return False


def handle_peer_request(conn, addr):
    """Handle incoming download requests from other peers"""
    try:
        data = conn.recv(1024).decode()
        parts = data.split()
        
        if len(parts) >= 5 and parts[0] == "START" and parts[1] == "DOWNLOAD":
            filename = parts[2]
            start_byte = int(parts[3])
            end_byte = int(parts[4])
            
            filepath = os.path.join(REPOSITORY_PATH, filename)
            
            if os.path.exists(filepath):
                bytes_to_read = end_byte - start_byte + 1
                print(f"Reading {filename}: bytes {start_byte} to {end_byte} ({bytes_to_read} bytes)")
                with open(filepath, 'rb') as f:
                    f.seek(start_byte)
                    file_data = f.read(bytes_to_read)
                    conn.send(file_data)
                print(f"Sent {len(file_data)} bytes of {filename} to {addr}")
            else:
                print(f"File {filename} not found")
        
        conn.close()
    except Exception as e:
        print(f"Error handling peer request: {e}")
        conn.close()


def peer_server():
    global client_port
    """Server thread to handle incoming requests from other peers"""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('127.0.0.1', 0))
    client_port = server_sock.getsockname()[1]


    server_sock.listen(5)
    print(f"Peer server listening on port {client_port}")
    
    while True:
        try:
            conn, addr = server_sock.accept()
            thread = threading.Thread(target=handle_peer_request, args=(conn, addr), daemon=True)
            thread.start()
        except Exception as e:
            print(f"Error accepting connection: {e}")


def parse_schedule(schedule_file):
    """Parse the schedule file"""
    tasks = []
    wait_time = 0
    
    try:
        with open(schedule_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('wait'):
                    wait_time = int(line.split()[1])
                elif ':' in line:
                    parts = line.split(':')
                    filename = parts[0]
                    filesize = int(parts[1])
                    tasks.append((filename, filesize))
        return wait_time, tasks
    except Exception as e:
        print(f"Error parsing schedule: {e}")
        return 0, []


def main():
    global client_port, server_socket_conn
    
    # Create socket and bind to get port
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(("", 0))
    #client_port = client_socket.getsockname()[1]
    
    # Start peer server thread
    server_thread = threading.Thread(target=peer_server, args=(), daemon=True)
    server_thread.start()
    
    # Connect to main server
    client_socket.connect((MAIN_SERVER_IP, MAIN_SERVER_PORT))
    server_socket_conn = client_socket
    print(f"Connected to server at {MAIN_SERVER_IP}:{MAIN_SERVER_PORT}")
    
    # Send SERVING message
    message = f"START SERVING {client_port} END"
    client_socket.send(message.encode())
    print(f"Sent: {message}")
    
    # Send initial PROVIDING message for all files in repository
    local_files = get_local_files()
    if local_files:
        for file in local_files:
            send_providing_message(file)
            time.sleep(0.1)  # Small delay between messages
    
    # Parse schedule
    wait_time, tasks = parse_schedule(SCHEDULE_FILE)
    
    # Wait as specified in schedule
    if wait_time > 0:
        print(f"Waiting {wait_time}ms before starting downloads...")
        time.sleep(wait_time / 1000.0)
    
    # Additional safety wait to ensure all peers have registered
    time.sleep(2)
    
    # Download files according to schedule
    for filename, filesize in tasks:
        print(f"Downloading {filename} ({filesize} bytes)")
        
        # Search for providers
        providers = search_file(filename)
        
        if providers:
            # Download file in parallel
            if download_file_parallel(providers, filename, filesize):
                # Notify server about new file
                send_providing_message(filename)
                time.sleep(0.5)  # Give time for message to be processed
        else:
            print(f"No providers found for {filename}")
    
    # Create 'done' file
    with open('done', 'w') as f:
        f.write('completed\n')
    print("All downloads completed. Created 'done' file.")
    
    # Keep the peer running to serve files
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down peer...")
        client_socket.close()


if __name__ == "__main__":
    main()