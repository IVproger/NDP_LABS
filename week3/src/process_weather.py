# import the necessary packages
import zmq
import json
import threading
import sys
from collections import deque

# Define the IP address and port number
IP_ADD = '127.0.0.1'
WEATHER_INPUT_PORT = 5555
CLIENT_INPUT_PORT = 5556

# Queue to store the last 30 sec data
latest_data = deque(maxlen=30)

# function to calculate the average temperature and humidity
def average_temperature_humidity():
    temperatures = [data['temperature'] for data in latest_data]
    humidities = [data['humidity'] for data in latest_data]
    return round(sum(temperatures) / len(temperatures),2), round(sum(humidities) / len(humidities),2)

# generate recommendation based on the average temperature
def recommendation(avg_temp):
    if avg_temp < 10:
        return "Today weather is cold. Its better to wear warm clothes"
    elif 10 <= avg_temp < 25:
        return "Feel free to wear spring/autumn clothes"
    else:
        return "Go for light clothes"

# handle the client requests
def handle_client_requests(socket):
    try:
        while True:
            message = socket.recv_string()
            if message == "Fashion":
                avg_temp, _ = average_temperature_humidity()
                recommendation_msg = recommendation(avg_temp)
                print(recommendation_msg)
                socket.send_string(recommendation_msg)
            elif message == "Weather":
                avg_temp, avg_humidity = average_temperature_humidity()
                print(
                    f"The last 30 sec average Temperature: {avg_temp}, Average humidity: {avg_humidity}")
                socket.send_string(
                    f"Average temperature: {avg_temp}, Average humidity: {avg_humidity}")
            else:
                socket.send_string("Query Not Found")
    except KeyboardInterrupt:
        print("Shutting down")
        socket.close()
        sys.exit(0)

# handle the weather data
def receive_weather_data(socket):
    try:
        while True:
            message = socket.recv_string()
            topic, data = message.split(' ', 1)
            data = json.loads(data)
            latest_data.append(data)
            print(f"Received weather data: {topic} {data}")
            with open('weather_data.log', 'a') as f:
                f.write(json.dumps(data) + '\n')
    except KeyboardInterrupt:
        print("Shutting down")
        socket.close()
        sys.exit(0)

# main function
def main():
    # define the ZeroMQ context and socket
    context = zmq.Context()
    client_socket = context.socket(zmq.REP)
    # Receive the client requests
    client_socket.bind(f"tcp://{IP_ADD}:{CLIENT_INPUT_PORT}")
    weather_socket = context.socket(zmq.SUB)
    # Subscribe to the weather data
    weather_socket.connect(f"tcp://{IP_ADD}:{WEATHER_INPUT_PORT}")
    weather_socket.setsockopt_string(zmq.SUBSCRIBE, "weather")

    # Start the threads
    threading.Thread(target=receive_weather_data,
                     args=(weather_socket,),).start()
    threading.Thread(target=handle_client_requests,
                     args=(client_socket,),).start()
    


if __name__ == "__main__":
    main()
