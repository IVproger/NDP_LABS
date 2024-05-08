# Import the necessary libraries
import argparse
import os
import socket
import signal


# Define the buffer size and the maximum segment size
BUFFER_SIZE = 20480
MSS = BUFFER_SIZE - 4


# Class to track the user session
class UserSession:
    def __init__(self, address, seq_num, file_name, file_size):
        self.address = address
        self.seq_num = seq_num
        self.file_name = file_name
        self.file_size = file_size
        self.chunks_got = 0

# Handle the keyboard interrupt
def signal_handler(sig, frame):
    if sig == signal.SIGINT:
        print(f"('0.0.0.0', {PORT}): Shutting down...")
        exit()

# Main function
if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="UDP server that receives file")
    parser.add_argument("port", type=int, help="The port number")
    parser.add_argument("max_clients", type=int, help="The maximum number of clients.")
    args = parser.parse_args()

    # Define the server address
    PORT = args.port
    server_address = ('0.0.0.0', PORT)

    # Track the sessions for each client
    sessions = {}

    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as sock:
        sock.bind(server_address)
        print(f"('0.0.0.0', {PORT}): Listening...")

        while True:
            # Handle the keyboard interrupt
            signal.signal(signal.SIGINT, signal_handler)

            try:
                # Get the data and address from the client
                data, address = sock.recvfrom(BUFFER_SIZE)

                # Define the message type
                message_type = chr(data[0])
                
                # Get the sequence number
                try:
                    seq_num = int(chr(data[2]))
                except:
                    print("Error: invalid data type received")
                    sock.close()
                    exit()

                # Process the message
                if message_type == 's':
                    # If the address is already in the sessions dictionary
                    if address in sessions:
                        ack_message = f'a|{(seq_num + 1) % 2}'
                        sock.sendto(ack_message.encode('utf-8'), address)
                        continue
                    
                    # Print the message
                    print(f"{address}: {data.decode('utf-8')}")

                    # Check if the server is overloaded
                    if len(sessions) < args.max_clients:
                        decoder = data.decode('utf-8').split('|')

                        if address not in sessions:
                            # Create the user session
                            file_name = decoder[2]
                            file_size = int(decoder[3])

                            # Add the session to the sessions dictionary
                            sessions[address] = UserSession(address, seq_num, file_name, file_size)

                        # Create the file to write the data
                        if os.path.isfile(file_name):
                            print(f"{address}: File: {file_name} will be overwritten")
                        open(file_name, 'wb').close()

                        # Send the ACK message
                        ack_message = f'a|{(seq_num + 1) % 2}'
                        sock.sendto(ack_message.encode('utf-8'), address)

                        # Change the sequence number in the session
                        sessions[address].seq_num = (seq_num + 1) % 2
                    else:
                        # Server is overloaded send negative ACK
                        ack_message = f'n|{(seq_num + 1) % 2}'
                        sock.sendto(ack_message.encode('utf-8'), address)
                        print(f"{address}: Server is overloaded, exiting...")

                elif message_type == 'd':
                    # Check if the address is in the sessions dictionary
                    if address not in sessions:
                        # Send a negative ACK
                        ack_message = f'n|{(seq_num + 1) % 2}'
                        sock.sendto(ack_message.encode('utf-8'), address)
                        continue

                    # decode only characters like d|0|chunk{number_of_chunk}
                    decoded_message = data[:4].decode('utf-8')

                    # Check if the sequence number matches the expected sequence number
                    if seq_num != sessions[address].seq_num:
                        ack_message = f'n|{(seq_num + 1) % 2}'
                        sock.sendto(ack_message.encode('utf-8'), address)
                        continue

                    # Print the message
                    print(f"{address}: {decoded_message}chunk{sessions[address].chunks_got + 1}")

                    # Get the chunk of data
                    chunk = data[4:]

                    # Increment the chunk id
                    sessions[address].chunks_got += 1

                    # Write the chunk to the file
                    with open(sessions[address].file_name, 'ab') as file:
                        file.write(chunk)

                    # Send the ACK message
                    ack_message = f'a|{(seq_num + 1) % 2}'
                    sock.sendto(ack_message.encode('utf-8'), address)

                    # Change the sequence number in the session
                    sessions[address].seq_num = (seq_num + 1) % 2

                    # Check if the file is complete
                    if os.path.getsize(sessions[address].file_name) == sessions[address].file_size:
                        print(f"{address}: Received {sessions[address].file_name}.")

                        # Remove the session from the sessions dictionary
                        del sessions[address]

                # If we receive an invalid data type from the client
                else:
                    ack_message = f'n|{(seq_num + 1) % 2}'
                    sock.sendto(ack_message.encode('utf-8'), address)
                    print("Error: invalid data type received")
                    sock.close()
                    exit()

            # Throw an exception if the user presses CTRL+C
            except KeyboardInterrupt:
                print(f"('0.0.0.0', {PORT}): Shutting down...")
                sock.close()
                exit()
