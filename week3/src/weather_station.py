# import the necessary packages
import zmq
import time
import json
import random
from datetime import datetime

# define the IP address and port number
IP_ADD = '127.0.0.1'
DATA_PROCESSES_INPUT_PORT = 5555

# function to generate weather data
def generate_weather_data():
    temperature = random.uniform(5, 40)
    humidity = random.uniform(40, 100)
    
    # round the values to 2 decimal places
    temperature = round(temperature, 2)
    humidity = round(humidity, 2)
    return json.dumps({"time": str(datetime.now()), "temperature": temperature, "humidity": humidity})

# function to generate CO2 data
def generate_co2_data():
    co2 = random.uniform(300, 500)
    # round the values to 2 decimal places
    co2 = round(co2, 2)
    return json.dumps({"time": str(datetime.now()), "co2": co2})

# main function
def main():
    # define the ZeroMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://{IP_ADD}:{DATA_PROCESSES_INPUT_PORT}")
    try:
        while True:
            time.sleep(2)
            # get the weather data and CO2 data
            weather_data = generate_weather_data()
            co2_data = generate_co2_data()
            
            # Send the data to the data processes
            socket.send_string(f"weather {weather_data}")
            print(f"Weather is sent from WS {weather_data}")
            socket.send_string(f"co2 {co2_data}")
            print(f"CO2 is sent from WS {co2_data}")
    
    # keyboard interrupt
    except KeyboardInterrupt:
        print("The weather station is shutting down...")
        socket.close()
        context.term()

if __name__ == '__main__':
    main()