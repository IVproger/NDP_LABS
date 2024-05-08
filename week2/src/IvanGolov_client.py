# Import necessary libraries
import os
import socket
import time
from multiprocessing import Pool, cpu_count
import threading

# Statistics 

# Before optimization      
# Files download time: 158.33495526099978
# Sorting time: 18.054982579998978

# After oprimization
# Files download time: 65.5063289259997
# Sorting time: 7.870921506000741

# Server URL and port
SERVER_URL = '127.0.0.1:12345'
# Buffer size for client
CLIENT_BUFFER = 1024
# Number of unsorted files to be downloaded
UNSORTED_FILES_COUNT = 100
# Maximum number of processes
MAX_PROCESSES = min(20, cpu_count())
MAX_THREADS = 25

def create_directories():
    # Create directories for unsorted and sorted files if they do not exist
    if not os.path.exists('unsorted_files'):
        os.mkdir('unsorted_files')
    if not os.path.exists('sorted_files'):
        os.mkdir('sorted_files')

def download_file(i):
    # Download file from server and save it to 'unsorted_files' directory
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ip, port = SERVER_URL.split(':')
        s.connect((ip, int(port)))
        file = b''
        while True:
            packet = s.recv(CLIENT_BUFFER)
            if not packet:
                break
            file += packet
        with open(f'unsorted_files/{i}.txt', 'wb') as f:
            f.write(file)

def sort_file(i):
    # Read unsorted file, sort the numbers and save it to 'sorted_files' directory
    with open(f"unsorted_files/{i}.txt", "r") as unsorted_file:
        unsorted_list = [int(number) for number in unsorted_file.read().split(',')]
        sorted_list = sorted(unsorted_list)
        with open(f"sorted_files/{i}.txt", "w") as sorted_file:
            sorted_file.write(','.join(map(str, sorted_list)))

def download_unsorted_files():
    # Download unsorted files concurrently using threading
    threads = []
    i = 0
    while i < UNSORTED_FILES_COUNT:
        if threading.active_count() <= MAX_THREADS:
            thread = threading.Thread(target=download_file, args=(i,))
            thread.start()
            threads.append(thread)
            i += 1
        else:
            time.sleep(10)
    # Wait for all threads to finish
    for thread in threads:
        thread.join()

def create_sorted_file():
    # Sort files in parallel using multiprocessing Pool
    with Pool(MAX_PROCESSES) as pool:
        pool.map(sort_file, range(UNSORTED_FILES_COUNT))

if __name__ == '__main__':
    # Create directories for unsorted and sorted files
    create_directories()

    # Measure and print the time taken to download unsorted files
    tdownload0 = time.monotonic()
    download_unsorted_files()
    tdownload = time.monotonic() - tdownload0
    print(f"Files download time: {tdownload}")

    # Measure and print the time taken to sort files
    tsort0 = time.monotonic()
    create_sorted_file()
    tsort = time.monotonic() - tsort0
    print(f"Sorting time: {tsort}")
