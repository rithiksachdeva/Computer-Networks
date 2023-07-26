# UC Davis Computer Networks - Fall 2022
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

## Project 1 Summary: Insights into Network Activity
This Python script reads and analyzes PCAP files. The script uses the dpkt library to parse the PCAP file and counts the number of TCP and UDP packets, as well as packets sent via HTTP, HTTPS, DNS, FTP, SSH, DHCP, TELNET, SMTP, POP3, and NTP. It also identifies unique destination IPs, providing insights into network activity.

## Project 2 Summary: Building an efficient DNS  Client
**Part 1**: Created a DNS Client that builds a DNS request for a Type A resource record according to RFC 1035, Section 4 and then uses Sockt API (sendto(), recvfrom()) to send and receive from public DNS resolvers. To run, pass in the hostname as an argument in the command line. Once response is received, it is unpacked and then returns the IP address of the resolved hostname. Further, goes to the IP address found and returns a html file of the webpage. 

**Part 2**: Create a DNS Client that this time implements the iterative strategy: creates a DNS request for a Type A record, starts from a given set of root servers, then decodes the response and resends the request to the TLD server IP stored in the response from the root server, and finally send the request again to the Authoritative server, which will send back the IP of the resolved hostname. Added bonus: computes and returns RTT. 

**Part 3**: Implements a DNS cache to reduce RTT of Part 2. Once IP is stores in cache, it stays until the TTL has run out, when its deleted.

## Project 3 Summary: Enhancing UDP with connection support, adding reliability, and implementing congestion control
### Part 1: Enhancing UDP with Connection Support (UDP Putah)
In this section of the project, I enhanced the basic functionality of the User Datagram Protocol (UDP) to incorporate key features from the Transmission Control Protocol (TCP). The resulting customized version of UDP, termed UDP Putah, aimed to mirror the reliability and connection-oriented attributes of TCP while still maintaining UDP's inherent simplicity and speed.
#### Skills and Concepts Employed
- Understanding of Network Protocols: I deepened my understanding of the fundamental differences between UDP and TCP. This project particularly focused on TCP's three-way handshake and its unique capability to establish persistent connections, which allows data transfer parallelization among multiple simultaneous users and enhances reliability.
- Implementation of TCP-like Features in UDP: I incorporated connection support in UDP, which traditionally doesn't support persistent connections. This involved implementing functionalities similar to TCP's "accept" and "connect" functions, followed by a three-way handshake between the client and the server.
- Socket Programming: I utilized advanced socket programming concepts, leading to the creation of two new UDP sockets (one each for the client and the server) for data communication, while the main threads reverted to accepting or connecting to new clients. This demonstrated a practical application of the difference between a welcoming socket and a connection socket.
- Custom TCP Header Design: I created a custom TCP header for the UDP Putah, keeping in mind the constraints of not introducing any additional fields beyond those in an actual TCP header and adhering to field size limits. This task reinforced my understanding of TCP headers and their role in facilitating network communication.
#### Learning Outcomes
This project was a deep dive into the internals of network protocols, specifically UDP and TCP. It enabled me to expand my knowledge about network sockets, connections, and headers, while also enhancing my Python programming skills, particularly in network programming and multi-threading. The knowledge gained from this project can be directly applied to designing and optimizing network applications for real-world use cases.

### Part 2: Adding Reliability to UDP Putah (UDP Solano)
In this phase of the project, my goal was to enhance the reliability of the previously developed UDP Putah, culminating in a more dependable version: UDP Solano. This was achieved by emulating TCP's acknowledgement process, which ensures message reliability via the use of cumulative acknowledgements.

#### Skills and Concepts Employed
- TCP-like Acknowledgement Process Implementation in UDP: In order to improve the reliability of UDP Solano, I introduced an acknowledgement process similar to TCP's. This involved confirming the number of bytes received by the receiver rather than acknowledging individual packets, known as cumulative acknowledgement. This feature was instrumental in making UDP Solano more reliable, mimicking the dependability of TCP.
- Simulated Packet Loss and Delay: To assess the resilience and performance of UDP Solano, I introduced artificial packet loss and delay conditions. I implemented these challenging conditions by generating random values for packet loss percentage and round trip jitter. This simulation created an environment mimicking real-world internet conditions, ensuring the robustness of the protocol developed.
- Handling Packet Loss and Timeout Adjustments: By introducing packet loss in the system, I learned how to design systems that could successfully resend lost packets. Additionally, I implemented a dynamic timeout mechanism, employing a formula to calculate the timeout interval based on previous Round Trip Times (RTTs), to account for variable packet delivery times.
- Multi-client File Transfer: Building on the multi-client handling capability developed in the previous project phase, I facilitated simultaneous file transfers from multiple clients. This feature ensures that UDP Solano can handle multiple clients without any interference or data loss.

#### Learning Outcomes
This phase of the project greatly expanded my understanding of reliable data transfer protocols and their operation under varying network conditions. The implementation of cumulative acknowledgements, induced packet loss and delay, and dynamic timeouts in UDP deepened my grasp of network programming and protocol design. The experience of handling multiple clients simultaneously further developed my ability to design and manage complex systems that can handle multiple tasks concurrently. These acquired skills are directly applicable to developing and optimizing real-world networking applications for performance and reliability.

### Part 3: Implementing Congestion Control in UDP Solano (UDP Berryessa)
The final phase of this project entailed extending UDP Solano to include a flavor of congestion control, effectively evolving it into a connection-oriented, reliable, congestion-controlled protocol: UDP Berryessa. This adaptation incorporated key features of TCP, such as the dynamic adjustment of packets sent and the ability to control congestion in a manner akin to TCP Tahoe and TCP Reno.

#### Skills and Concepts Employed
- Congestion Control Incorporation: Drawing upon knowledge acquired from lectures, discussions, and supplemental readings, I infused congestion control into UDP Solano, following the TCP Tahoe and TCP Reno models. This involved sending more than a single packet at a time and adjusting packet transmission based on network congestion.

- Terminal Argument Implementation: I introduced an additional terminal argument, the Bandwidth-Delay Product (BDP), representing the maximum amount of data that could be sent on the network at one go. By monitoring the sender's data rate, the receiver could detect congestion if the sender's rate surpassed the BDP.

- Congestion State Handling: I formulated a method for handling network congestion by tripling the packet loss percentage and the receiver's sleep time when round-trip jitter conditions were met. This emulated TCP's response to network congestion, allowing for more stable and reliable data transfer even under high traffic.

- TCP Tahoe and Reno Implementation: By incorporating the principles of TCP Tahoe and Reno on the sender's side, I enhanced the protocol's congestion management capabilities. This involved the development of a variable timeout interval based on network conditions and the ability to switch between TCP versions via a terminal switch.

- Multi-client Data Transfer: Like the previous phase, this stage also required simultaneous file transfers from multiple clients using varying TCP versions. This was to ensure that UDP Berryessa could handle multiple clients simultaneously without any disruption or loss of data.

#### Learning Outcomes
This phase of the project enhanced my understanding of congestion control in reliable data transfer protocols, particularly how network conditions can be dynamically adjusted to optimize data transmission. Implementing TCP Tahoe and Reno's principles in a UDP protocol honed my abilities in network programming, protocol design, and traffic management. The ability to develop a robust, reliable, and congestion-controlled protocol like UDP Berryessa deepened my comprehension of critical networking concepts and equipped me with the skills to design and optimize networking applications in real-world scenarios.
