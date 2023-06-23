import socket

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# set the IP address and port number to send the packet
ip_address = '10.0.0.2'
port_number = 12345

# connect to the remote host
s.connect((ip_address, port_number))

# send data via TCP packet
data = b'Hello, world!'
s.send(data)

# close the connection
s.close()