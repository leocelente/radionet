from scapy.layers.inet import ICMP, IP
from scapy.all import sr
sr(IP(dst="10.0.0.2/32")/ICMP(), timeout=3)