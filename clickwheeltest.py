import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0",9090))

while True:
    data, addr = sock.recvfrom(3)
    button, state, wheel_pos = data
    print(button, state, wheel_pos)