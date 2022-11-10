import sys
import socket
import binascii
import time

def getQuestionPartlength(message, qSectionStart):
    length = 0
    endQuestion = 0
    while endQuestion == 0 or message[endQuestion:endQuestion+2] != "00" or endQuestion > len(message):
        lengthOfQ = message[qSectionStart:qSectionStart + 2]
        if len(lengthOfQ) == 0:
            return 0
        endQuestion = qSectionStart + 2 + (int(lengthOfQ, 16) * 2)
        length += len(message[qSectionStart + 2:endQuestion])
        qSectionStart = endQuestion
    return(length)
        

def decodeMessage(message):    
    
    #Question Section Starts on bit 24, so is passed in --> getQuestionPartlength is based on the parts of the question, which can be found as part of the question bits and depends on hostname. Thus, where the answer
    # section begins is dynamic as it depends on where the Q bits end 
    startAnsBit = 24 + getQuestionPartlength(message, 24) + 14

    if (startAnsBit < len(message)):
        recordType = message[startAnsBit + 4:startAnsBit + 8]
        TTL = int(message[startAnsBit + 12:startAnsBit + 20], 16)
        rdataLength = int(message[startAnsBit + 20:startAnsBit + 24], 16)
        IP = message[startAnsBit + 24:startAnsBit + 24 + (rdataLength * 2)]
        ipOctets = [IP[i:i+2] for i in range(0, len(IP), 2)]
        IP_decoded = ".".join(list(map(lambda x: str(int(x, 16)), ipOctets)))
        
        print("HTTP Server IP address: " + IP_decoded)

    return IP_decoded

def encodeMessage(hostname):
    ID = 12345
    QR = 0 
    OPCODE = 0 
    AA = 0 
    TC = 0 
    RD = 1 
    RA = 0 
    Z = 0 
    RCODE = 0 
    QDCOUNT = 1 
    ANCOUNT = 0 
    NSCOUNT = 0 
    ARCOUNT = 0 

    first2Rows = str(QR)
    first2Rows += str(OPCODE).zfill(4) #makes OPCODE into a 4 bit number by appending it with 0 until it has 4 digits
    first2Rows += str(AA)
    first2Rows += str(TC)
    first2Rows += str(RD)
    first2Rows += str(RA)
    first2Rows += str(Z).zfill(3) #makes Z into a 3 bit number 
    first2Rows += str(RCODE).zfill(4) #makes it into a 4 bit number
    first2Rows = "{:04x}".format(int(first2Rows, 2)) #converts the string into a integer of base 2, and then converts it into a 16 bit hexadecimal with 4 decimals

    header = ""
    header += "{:04x}".format(ID) #convert ID into a 16 bit hexadecimal with 4 digits
    header += first2Rows
    header += "{:04x}".format(QDCOUNT) #convert QDCOUNT into a 16 bit hexadecimal with 4 digits
    header += "{:04x}".format(ANCOUNT) #convert ANCOUNT into a 16 bit hexadecimal with 4 digits
    header += "{:04x}".format(NSCOUNT) #convert NSCOUNT into a 16 bit hexadecimal with 4 digits
    header += "{:04x}".format(ARCOUNT) #convert ARCOUNT into a 16 bit hexadecimal with 4 digits

    message = header

    #given tmz.com, we need to split it into [tmz,com] --> can be accomplished by split(".")
    hostnamesplit = hostname.split(".")
    for elem in hostnamesplit:
        length = "{:02x}".format(len(elem)) #turn the length into a 16 bit hexadecimal with 2 digits
        #print("addr segment:" + elem + " length:" + length)
        elem_part = binascii.hexlify(elem.encode()) 
        message += length
        message += elem_part.decode() 

    message += "00" # Terminating QNAME with a zero length octet?

    QTYPE = "{:04x}".format(1) #GETTING RR RECORD of type 'A'
    message += QTYPE
    QCLASS = "{:04x}".format(1) #class lookup is 1 for internet
    message += QCLASS      
                                 
    message = message.replace(" ", "")
    message = message.replace("\n","")
    return message

hostname = sys.argv[1]
print("Hostname:", hostname)
message = encodeMessage(hostname)
#print("\nRequest raw:\n" + message)
server_address = ("169.237.229.88", 53) # CHANGE RESOLVER HERE
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
startTimeResolver = time.time()
sock.sendto(binascii.unhexlify(message), server_address)
data, _ = sock.recvfrom(4096)
endTimeResolver = time.time()
#print("\nRTT for Resolver: " + str(endTimeResolver - startTimeResolver) + "\n")
sock.close()
response = binascii.hexlify(data).decode("utf-8")
#print("\nResponse raw:\n" + response)
decodedResponse = decodeMessage(response)

#print("TCP Connection")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((decodedResponse, 80))
hostname = hostname.encode('utf-8')
startHTTPget = time.time()
sock.send(b"GET / HTTP/1.1\r\nHost:" + hostname + b"\r\n\r\n")
response = sock.recv(4096)
endHTTPget = time.time()
#print("\nRTT for HTTP Server/Client: " + str(endHTTPget - startHTTPget) + "\n")
sock.close()
response = response.decode('utf-8')
#print(response)

text_file = open("PartA_http_Rithik Sachdeva_917131606_Rajveer Grewal_917628973.txt","w")
text_file.write(response)
text_file.close()


