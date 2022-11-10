# Project 1
- Given a PCAP file that is captured using Wireshark, analyze the file using dpkt library and find Type and Number of Packets sent via each protocol (HTTP, HTTPS,
DNS, FTP, SSH, DHCP, TELNET, SMTP, POP3,  and NTP). Finally, return the top 5 unique destination IPs.  

# Project 2
 - Part 1: Created a DNS Client that builds a DNS request for a Type A resource record according to RFC 1035, Section 4 and then uses Sockt API (sendto(), recvfrom()) to send and receive from public DNS resolvers. To run, pass in the hostname as an argument in the command line. Once response is received, it is unpacked and then returns the IP address of the resolved hostname. Further, goes to the IP address found and returns a html file of the webpage. 
 - Part 2: Create a DNS Client that this time implements the iterative strategy: creates a DNS request for a Type A record, starts from a given set of root servers, then decodes the response and resends the request to the TLD server IP stored in the response from the root server, and finally send the request again to the Authoritative server, which will send back the IP of the resolved hostname. Added bonus: computes and returns RTT. 
 - Part 3: Implements a DNS cache to reduce RTT of Part 2. Once IP is stores in cache, it stays until the TTL has run out, when its deleted. 
