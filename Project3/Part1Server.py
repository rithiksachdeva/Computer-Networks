#This file was created by Rithik Sachdeva
import threading
import binascii
import random
import socket

clientPort = []

def create_header(srcprt, destprt, seqnum, acknum, ack, syn, fin):

    srcPort = "{:04x}".format(srcprt)
    destPort = "{:04x}".format(destprt)
    sequenceNum = "{:08x}".format(seqnum)
    headerNum = "{:08x}".format(acknum)

    
    headerLength = format(0,"b").zfill(4) # 16 is 5 bits, not 4 which is making the message 129 bits instead of 128
    unused = format(0,"b").zfill(4)
    CWR = str(0)
    ECE = str(0)
    URG = str(0)
    ACK = str(ack)
    PSH = str(0)
    RST = str(0)
    SYN = str(syn)
    FIN = str(fin)

    flagsSection = headerLength + unused + CWR + ECE + URG + ACK + PSH + RST + SYN + FIN
    flagsSection = "{0:0>4X}".format(int(flagsSection, 2))

    rcvWnd = "{:04x}".format(0)
    
    header = srcPort + destPort + sequenceNum + headerNum + flagsSection + rcvWnd
    return(header)

def create_syn(src,dest):
    seq = random.randint(20000,30000)
    header = create_header(src,dest,seq,0,0,1,0)
    return(header)

def create_synack(src,dest,seq):
    ack = random.randint(40000,50000)
    header = create_header(src,dest,seq,ack,1,1,0)
    return(header)
    
def create_ack(src,dest,seq,ack):
    header = create_header(src,dest,seq,ack,1,0,0)
    return(header)

def create_fin(src,dest,seq,ack):
    header = create_header(src,dest,seq,ack,0,0,1)
    return(header)

def create_datahdr(src,dest,seq,ack):
    header = create_header(src,dest,seq,ack,0,0,0)
    return(header)

def create_datamessage(data,header):
    message = header +(binascii.hexlify(data.encode())).decode()
    return(message)

def decode_message(message):
    src = message[0:4]
    sourcePort = int('0x' + src,16)

    dest = message[4:8]
    destPort = int('0x' + dest,16)

    seqnum = message[8:16]
    seqNumber = int('0x' + seqnum,16)

    acknum = message[16:24]
    ackNumber = int('0x' + acknum,16)

    flags = message[24:28]
    interpretableFlags = (bin(int(flags,16))[2:]).zfill(16)
    if(interpretableFlags[11] == '1' and interpretableFlags[14] == '1'):
        msgType = 'SYN/ACK'
    elif(interpretableFlags[11] == '1'):
        msgType = 'ACK'
    elif(interpretableFlags[14] == '1'):
        msgType = 'SYN'
    elif(interpretableFlags[15] == '1'):
        msgType = 'FIN'
    else:
        msgType = 'DATA'

    rcvWnd = message[28:32]
    rcvWndw = int('0x' + rcvWnd,16)

    data = message[32:]
    msgData = (binascii.unhexlify((data.encode()))).decode()

    return(sourcePort,destPort,seqNumber,ackNumber,msgType,rcvWndw,msgData)

def signal_handler(sig,frame):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    finPort = sock.getsockname()[1]

    for port in clientPort:
        finheader = create_fin(finPort,port,0,0)
        sock.sendto(finheader,('127.0.0.1',port))
        msgtype = 'FIN'
        count = 1
        while msgtype != 'ACK' or count != 3
            ack, _ = sock.recvfrom(4096)
            src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(ack)
            count+=1
    sys.exit(0)

def accept():
    #open welcome socket at localhost:8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 8000))

    while True:
        #look for syn message
        syn, _ = sock.recvfrom(4096)
        #decode syn message
        src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(syn)
        if(msgtype == 'SYN'):
            #create a new server connection socket
            connectsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #bind the server connection socket to a random port
            connectsock.bind(('', 0))
            #get the port number of the new connection socket so it can be sent back to client
            newPort = connectsock.getsockname()[1]
            #create a synack header (no need for message) with src = 8000, dest as newPort and seqnum = seqnum +1
            synackMsg = create_synack('8000',newPort, str(int(seq) + 1))
            #send synack header to src of syn msg
            sock.sendto(synackMsg, ('127.0.0.1', src))
            #wait for response ack message
            ack, _ = sock.recvfrom(4096)
            #decode response ack message
            src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(ack)
            #create a new thread with the server new connect socket and the port of the new client socket
            thread = threading.Thread(target=connectionSocket, args=(connectsock,))
            #start the thread
            thread.start()
            

def connectionSocket(sock):
    signal.signal(signal.SIGINT, signal_handler)
    msgtype = 'DATA'
    while msgtype != 'FIN':
        recvmsg, _ = sock.recvfrom(4096)
        src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(recvmsg)
        if src not in clientPort:
            clientPort.append(src)
        if(src == clientport and msgtype == 'DATA'):
            header = create_datahdr(dest,src,ack,str(int(seq) + 4))
            message = create_datamessage('pong',header)
            sock.sendto(message, ('127.0.0.1', src))
    create_ack(dest,src,seq,ack)
    sock.close()
            
    
    
header = create_synack(1234, 80, 24951)
print(header)
message = create_datamessage("ping",header)
print(message)
src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(message)
print(src,dest,seq,ack,msgtype,rcvwnd,data)



    

