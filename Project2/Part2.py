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

    isAA = 0

    header_params  = message[4:8]
    header_params = "{:b}".format(int(header_params, 16)).zfill(16)
    if(header_params[5:6] == str(1)):
        #print("AA = " + header_params[5:6])
        isAA = 1
        
    #Question Section Starts on bit 24, so is passed in --> getQuestionPartlength is based on the parts of the question, which can be found as part of the question bits and depends on hostname. Thus, where the answer
    # section begins is dynamic as it depends on where the Q bits end 
    startAnsBit = 24 + getQuestionPartlength(message, 24) + 14

    if (startAnsBit < len(message)):
        recordType = message[startAnsBit + 4:startAnsBit + 8]
        rdataLength = int(message[startAnsBit + 20:startAnsBit + 24], 16)

    while((startAnsBit < len(message)) and (int(recordType,16)) != 1):
        startAnsBit = startAnsBit + 24 + (rdataLength * 2)
        recordType = message[startAnsBit + 4:startAnsBit + 8]
        rdataLength = int(message[startAnsBit + 20:startAnsBit + 24], 16)
    
    if (startAnsBit < len(message)):
        recordType = message[startAnsBit + 4:startAnsBit + 8]
        TTL = int(message[startAnsBit + 12:startAnsBit + 20], 16)
        rdataLength = int(message[startAnsBit + 20:startAnsBit + 24], 16)
        IP = message[startAnsBit + 24:startAnsBit + 24 + (rdataLength * 2)]
        ipOctets = [IP[i:i+2] for i in range(0, len(IP), 2)]
        IP_decoded = ".".join(list(map(lambda x: str(int(x, 16)), ipOctets)))

    return isAA, IP_decoded

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
    first2Rows += str(Z).zfill(3) #makes Z into a 3 bit number with 3 0s
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

def sendDNSreq(ip, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        startTimeRoot = time.time()
        sock.sendto(binascii.unhexlify(message), (ip,53))
        data, _ = sock.recvfrom(4096)
        endTimeRoot = time.time()
        sock.close()
        return data, startTimeRoot, endTimeRoot
    except:
        data = ""
        sock.close()
        return data, startTimeRoot, endTimeRoot

rootservers = ["198.41.0.4", "199.9.14.201", "192.33.4.12", "199.7.91.13"
               ,"192.203.230.10", "192.5.5.241", "192.112.36.4", "198.97.190.53"
               ,"192.36.148.17", "192.58.128.30", "193.0.14.129", "199.7.83.42"
               ,"202.12.27.33"]
hostname = sys.argv[1]
print("Domain:", hostname)
message = encodeMessage(hostname)
#print("\nRequest raw:\n" + message)
rootCount = 0
data = ""
while(data == "" and rootCount < 12):
    data, startTimeRoot, endTimeRoot = sendDNSreq(rootservers[rootCount], message)
    rootCount = rootCount + 1
print("Root server IP address:", str(rootservers[rootCount-1]))
#print("Connected to Root Server at ip " + str(rootservers[rootCount-1]))
#print("\nRTT for Root Server: " + str(endTimeRoot - startTimeRoot) + "\n")

serverList = []
if data == "":
    exit
response = binascii.hexlify(data).decode("utf-8")
#print("\nResponse raw:\n" + response)
isAuthoritative, decodedResponse = decodeMessage(response)
while isAuthoritative == 0:
    #print("Connecting to server at: " + str(decodedResponse))
    serverList.append(str(decodedResponse))
    data, startTimeResolver, endTimeResolver = sendDNSreq(decodedResponse, message)
    if data == "":
        exit
    #print("\nRTT for other DNS Server: " + str(endTimeResolver - startTimeResolver) + "\n")
    response = binascii.hexlify(data).decode("utf-8")
    isAuthoritative, decodedResponse = decodeMessage(response)

#print("IP ADDRESS RECVED FROM AUTH SERVER: " + str(decodedResponse))
print("TLD server IP address:", serverList[0])
print("Authoritative server IP address:", serverList[1])
print("HTTP server IP address:", decodedResponse)

