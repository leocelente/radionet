echo "Creating a pipe between /dev/ttyS20 and /dev/ttyS21"
sudo socat pty,raw,echo=0,link=/dev/ttyS20 pty,raw,echo=0,link=/dev/ttyS21