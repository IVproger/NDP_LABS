kill -9 $(lsof -t -i:8080)
python3 server.py 8080
