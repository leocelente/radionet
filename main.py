from argparse import ArgumentParser
from select import select
from configparser import ConfigParser
from kiss import KISS, CMD_DATA
from tunnel import SerialTunnel
from rich.console import Console
from scapy.all import hexdump, Raw
from scapy.layers.inet import IP
from datetime import datetime

parser = ArgumentParser("RadioNet")
parser.add_argument('config', type=str)
args = parser.parse_args()

config = ConfigParser()
config.read(args.config)
cfg = config['interface']

tunnel = SerialTunnel(
    name=       cfg['name'],
    tty=        cfg['tty'],
    baud=       int(cfg['baud']),
    mtu=        int(cfg['mtu']),
    peer_ip=    cfg['peer'],
    ip=         cfg['ip']
)

console = Console()

def check_chksum(packet: IP) -> bool:
    original_checksum = packet.chksum
    del packet.chksum
    recomputed_checksum = IP(bytes(packet)).chksum
    return original_checksum == recomputed_checksum    

def is_valid_ip_packet(packet) -> bool:
    # Use checksum to differentiate RAW socket data from normal IP packets
    return hasattr(packet, 'chksum') and (packet.chksum is not None) and check_chksum(packet)

def is_multicast(packet: IP) -> bool:
    start = int(packet.dst.split('.')[0])
    return start >= 224 and start <= 239; 
    

def on_ip_data(data: bytes) -> None:
    size = len(data)
    packet = IP(data)
    timestamp = datetime.now().strftime("%Hh%Mm%Ss")
    if is_valid_ip_packet(packet):
        # In theory we disable multicast to this interface, but they seem to come in anyway
        if is_multicast(packet): 
            console.print(f"[red]\[{timestamp}]({size}) {packet.summary()}")
            return

        console.print(f"[green]\[{timestamp}]({size}) {packet.summary()}\n{hexdump(packet, True)}\n ")    
    else:
        packet = Raw(data)
        console.print(f"[blue]\[{timestamp}]({size}) {packet.summary()}\n{hexdump(packet, True)}\n")

    tunnel.serial.write(KISS.transform(CMD_DATA, data))
    

def on_serial_data(cmd_type, data: bytes) -> None:
    size = len(data)
    try:
        packet = IP(data)
    except TypeError:
        console.print(data)
        packet = Raw(data)
    timestamp = datetime.now().strftime("%Hh%Mm%Ss")
    if is_valid_ip_packet(packet) and int.from_bytes(cmd_type, byteorder='big') == CMD_DATA:
        console.print(f"[bright_cyan]\[{timestamp}]({size}) {packet.summary()}\n{hexdump(packet, True)}\n ")
        tunnel.tun.write(data)
    else:
        # Deal with incoming RAW packets or CMD_CONF
        console.print(f"[bright_magenta]\[{timestamp}]({size}) Raw <{cmd_type}>\n{hexdump(data, True)}\n")
        pass
        

kiss = KISS(callback=on_serial_data)

try:
    while True:
        readers, _, _ = select([tunnel.tun, tunnel.serial], [], [])
        for reader in readers:
            if reader is tunnel.tun:
                on_ip_data(reader.read(tunnel.tun.mtu))
            elif reader is tunnel.serial:
                kiss.ingest(reader.read(1))
            else:
                print(f"select() fail {reader}")
                tunnel.close()
                exit(1)
            
except KeyboardInterrupt:
    print("Exiting...")
    tunnel.close()