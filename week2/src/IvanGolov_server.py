# Import the necessary modules
import socket
import threading
import random

# Define the port and server address
PORT = 12345
server_address = ('0.0.0.0', PORT)

# Define the maximum number of random numbers to generate and send to the client
MAX_NUMBERS = 250000

def send_str_to_client(client_socket):
    # Generate a list of random numbers
    numbers = [random.randint(-999999999, 999999999) for _ in range(MAX_NUMBERS)]
    # Convert the list of numbers to a comma-separated string
    numbers_str = ','.join(map(str, numbers))
    print(f"Send to {client_socket.getpeername()}")
    # Send the string of numbers to the client
    client_socket.send(numbers_str.encode())
    # Close the client socket
    client_socket.close()

# Create a TCP/IP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Allow the server to use the same address even if it's still in TIME_WAIT state
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the server address
    server_socket.bind(server_address)
    print(f"Listening on 0.0.0.0:{PORT}")
    # Listen for incoming connections
    server_socket.listen()
    try:
        while True:
            # Accept a new connection
            client_socket, addr = server_socket.accept()
            # Start a new thread to handle the connection
            client_thread = threading.Thread(target=send_str_to_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        # If the server is interrupted, close the socket and exit
        print("Shutting down...")
        server_socket.close()
        exit(0)