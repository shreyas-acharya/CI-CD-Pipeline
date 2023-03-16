import socket
import time
import sys

timeout = 3

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

for _ in range(10):
    result = sock.connect_ex(("0.0.0.0", 8000))
    if result == 0:
        sys.exit(0)
    else:
        print("waiting ...")
        time.sleep(timeout)
sys.exit(1)
