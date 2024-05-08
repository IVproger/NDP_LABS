# import the necessary packages
import zmq
import json

# define the IP address and port number
WEATHER_INPUT_PORT= 5555
IP_ADD = '127.0.0.1'

def main():
    # get the context of the zmq
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{IP_ADD}:{WEATHER_INPUT_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "co2")
    try:
        while True:
            # receive the message from the weather station
            message = socket.recv_string()
            topic, data = message.split(' ', 1)
            data = json.loads(data)
            print(f"Received weather data: {topic} {data}")
            # log the data to the file
            with open('co2_data.log', 'a') as f:
                f.write(json.dumps(data) + '\n')
            if data['co2'] > 400:
                print("Danger Zone! Please do not leave home")
                
    # keyboard interrupt
    except KeyboardInterrupt:
        print("The CO2 process is shutting down...")
        socket.close()
        context.term()

if __name__ == "__main__":
    main()