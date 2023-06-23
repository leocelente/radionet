from pytun import TunTapDevice, IFF_NO_PI, IFF_TUN
from serial import Serial
import os

class SerialTunnel():
    
    tun: TunTapDevice
    serial: Serial
    peer: str
    

    def __init__(self, name: str, tty: str, baud: int=115200, ip: str='10.0.0.1', mtu: int=296, peer_ip:str='10.0.0.2') -> None:
        """Create Tunnel Interface connecting to Serial Port

        Args:
            name (str): Name of the Network Interface 
            tty (str): Name of the Serial Port to use
            baud (int, optional): Serial Port BaudRate. Defaults to 115200.
            ip (str, optional): Host IP Address. Defaults to '10.0.0.1'.
            mtu (int, optional): Maximum Transfer Unit of the Interface. Defaults to 296.
            peer_ip (str, optional): Peer IP Address. Defaults to '10.0.0.2'.
        """
        # Create Interface as TUN device, working on Layer 3 IP packets only
        # IFF_NO_PI removes redundant destination IP prefix on packet
        self.tun = TunTapDevice(name=name, flags=IFF_TUN|IFF_NO_PI)
        self.tun.addr = ip
        self.tun.mtu = mtu
        self.tun.netmask = '255.255.255.255'
        self.peer = peer_ip
        # Timeout is needed to prevent hangup when line is idle
        self.serial = Serial(port=tty, baudrate=baud, timeout=10/baud)
        self.tun.up()
        self._ifconfig()
        self._ethtool()


    
    def _ifconfig(self):
        """Uses Unix 'ifconfig' to configure TUN Interface as point-to-point
        """
        os.system(f"sudo ip link set multicast off dev {self.tun.name}")
        os.system(f"sudo ifconfig {self.tun.name} {self.tun.addr} pointtopoint {self.peer} up ")


    def _ethtool(self):
        """Uses 'ethtool' to configure TUN Interface as low speed half-duplex
        """
        os.system(f"sudo ethtool -s {self.tun.name} speed 1 duplex half autoneg off")


    def close(self):
        self.tun.down()
        self.serial.close()