import dpkt
import datetime
import socket
from dpkt.compat import compat_ord

file = input("What file should we analyze?\n")
f = open(file, 'rb')
pcap = dpkt.pcap.Reader(f)

TCPcount = 0
UDPcount = 0
HTTPcount = 0
HTTPScount = 0
DNScount = 0
FTPcount = 0
SSHcount = 0
DHCPcount = 0
TELNETcount = 0
SMTPcount = 0
POP3count = 0
NTPcount = 0
uniquedestIPs = []
IPcount = []

for timestamp, buf in pcap:
    eth = dpkt.ethernet.Ethernet(buf)

    if not isinstance(eth.data, dpkt.ip.IP):
        #print('Non IP Packet type not supported %s\n' % eth.data.__class__.__name__)
        continue

    ip = eth.data

    if isinstance(ip.data, dpkt.tcp.TCP):
        TCPcount = TCPcount + 1

        tcp = ip.data
        if tcp.sport == 80 or tcp.dport == 80:
            HTTPcount = HTTPcount + 1
        elif tcp.sport == 443 or tcp.dport == 443:
            HTTPScount = HTTPScount + 1
        elif tcp.sport == 53 or tcp.dport == 53:
            DNScount = DNScount + 1
        elif tcp.sport == 20 or tcp.dport == 20 or tcp.sport == 21 or tcp.dport == 21:
            FTPcount = FTPcount + 1
        elif tcp.sport == 22 or tcp.dport == 22:
            SSHcount = SSHcount + 1
        elif tcp.sport == 67 or tcp.dport == 67 or tcp.sport == 68 or tcp.dport == 68:
            DHCPcount = DHCPcount + 1
        elif tcp.sport == 23 or tcp.dport == 23:
            TELNETcount = TELNETcount + 1
        elif tcp.sport == 25 or tcp.dport == 25 or tcp.sport == 587 or tcp.dport == 587:
            SMTPcount = SMTPcount + 1
        elif tcp.sport == 110 or tcp.dport == 110:
            POP3count = POP3count + 1
        elif tcp.sport == 123 or tcp.dport == 123:
            NTPcount = NTPcount + 1
        
        exists = uniquedestIPs.count(socket.inet_ntop(socket.AF_INET, ip.dst))
        if exists > 0:
            exists = 0
            index = uniquedestIPs.index(socket.inet_ntop(socket.AF_INET, ip.dst))
            IPcount[index] = IPcount[index] + 1
        else:
            uniquedestIPs.append(socket.inet_ntop(socket.AF_INET, ip.dst))
            index = uniquedestIPs.index(socket.inet_ntop(socket.AF_INET, ip.dst))
            IPcount.append(1)
            exists = 0

    else:
        if ip.p == dpkt.ip.IP_PROTO_UDP:
            UDPcount = UDPcount + 1
            
            udp = ip.data
            if udp.sport == 80 or udp.dport == 80:
                HTTPcount = HTTPcount + 1
            elif udp.sport == 443 or udp.dport == 443:
                HTTPScount = HTTPScount + 1
            elif udp.sport == 53 or udp.dport == 53:
                DNScount = DNScount + 1
            elif udp.sport == 20 or udp.dport == 20 or udp.sport == 21 or udp.dport == 21:
                FTPcount = FTPcount + 1
            elif udp.sport == 22 or udp.dport == 22:
                SSHcount = SSHcount + 1
            elif udp.sport == 67 or udp.dport == 67 or udp.sport == 68 or udp.dport == 68:
                DHCPcount = DHCPcount + 1
            elif udp.sport == 23 or udp.dport == 23:
                TELNETcount = TELNETcount + 1
            elif udp.sport == 25 or udp.dport == 25 or udp.sport == 587 or udp.dport == 587:
                SMTPcount = SMTPcount + 1
            elif udp.sport == 110 or udp.dport == 110:
                POP3count = POP3count + 1
            elif udp.sport == 123 or udp.dport == 123:
                NTPcount = NTPcount + 1

            exists = uniquedestIPs.count(socket.inet_ntop(socket.AF_INET, ip.dst))
            if exists > 0:
                exists = 0
                index = uniquedestIPs.index(socket.inet_ntop(socket.AF_INET, ip.dst))
                IPcount[index] = IPcount[index] + 1
            else:
                uniquedestIPs.append(socket.inet_ntop(socket.AF_INET, ip.dst))
                index = uniquedestIPs.index(socket.inet_ntop(socket.AF_INET, ip.dst))
                IPcount.append(1)
                exists = 0
                
            
            

print("Number of TCP packets: " + str(TCPcount))
print("Number of UDP packets: " + str(UDPcount))
print("Number of packets sent via HTTP: " + str(HTTPcount))
print("Number of packets sent via HTTPS: " + str(HTTPScount))
print("Number of packets sent via DNS: " + str(DNScount))
print("Number of packets sent via FTP: " + str(FTPcount))
print("Number of packets sent via SSH: " + str(SSHcount))
print("Number of packets sent via DHCP: " + str(DHCPcount))
print("Number of packets sent via TELNET: " + str(TELNETcount))
print("Number of packets sent via SMTP: " + str(SMTPcount))
print("Number of packets sent via POP3: " + str(POP3count))
print("Number of packets sent via NTP: " + str(NTPcount))
print("Number of unique destination IPs:" + str(len(uniquedestIPs)))

res = sorted(range(len(IPcount)), key = lambda sub: IPcount[sub])[-5:]
for i in range(5):
    print(uniquedestIPs[res[i]])
