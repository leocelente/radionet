import socket

UDP_IP = "10.0.0.2"
UDP_PORT = 5005
MESSAGE = "Hello, World!"

print("IP:", UDP_IP)
print("port:", UDP_PORT)
print("message:", MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
socket.SOCK_DGRAM) # UDP
sock.sendto(bytes(MESSAGE, "utf-8"), (UDP_IP, UDP_PORT))
