#This file was created by Rithik Sachdeva
import threading
import binascii
import random
import socket
import sys
from datetime import datetime
import signal

serverip = sys.argv[2]
serverport = sys.argv[4]
clientPort = []
welcomeSocket = 0

def log(source,destination, messagetype, messagelength):
    dateTimeObj = datetime.now()
    currenttimestamp = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    logfile = open('log.txt', 'a')
    logfile.write(str(source) + " " + str(destination) + " " + str(messagetype) + " " + str(messagelength) + " " + currenttimestamp + "\n")
    logfile.close()

def create_header(srcprt, destprt, seqnum, acknum, ack, syn, fin, optionLength=0):

    srcPort = "{:04x}".format(int(srcprt))
    destPort = "{:04x}".format(int(destprt))
    sequenceNum = "{:08x}".format(int(seqnum))
    headerNum = "{:08x}".format(int(acknum))

    
    headerLength = format((int((16+optionLength) / 4)),"b").zfill(4)
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

def create_options(kind, length, data):
    kindfield = "{:02x}".format(kind)
    lengthfield = "{:02x}".format(length)
    datafield = "{:04x}".format(data)
    return kindfield+lengthfield+datafield

def create_synack(src,dest,acknum, connectionport):
    seqnum = random.randint(40000,50000)
    header = create_header(src,dest,seqnum,acknum,1,1,0,4)
    options = create_options(252,4, connectionport)
    return(header + options)
    
def create_ack(src,dest,seq,ack):
    header = create_header(src,dest,seq,ack,1,0,0)
    return(header)

def create_fin(src,dest,seq,ack):
    header = create_header(src,dest,seq,ack,0,0,1)
    return(header)

def create_datahdr(src,dest,seq,ack):
    header = create_header(src,dest,seq,ack,0,0,0)
    return(header)

def create_datamessage(src, dest, seqnum, acknum, data):
    header = create_datahdr(src, dest, seqnum, acknum)
    message = header +(binascii.hexlify(data.encode())).decode()
    return(message)

def decode_message(message):
    src = message[0:4]
    sourcePort = int('0x' + src.decode("utf-8"),16)

    dest = message[4:8]
    destPort = int('0x' + dest.decode("utf-8"),16)

    seqnum = message[8:16]
    seqNumber = int('0x' + seqnum.decode("utf-8"),16)

    acknum = message[16:24]
    ackNumber = int('0x' + acknum.decode("utf-8"),16)

    flags = message[24:28]
    interpretableFlags = (bin(int(flags,16))[2:]).zfill(16)
    headerLength = int(interpretableFlags[0:4],2) * 4
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
    rcvWndw = int('0x' + rcvWnd.decode("utf-8"),16)

    kind = 0
    length = 0
    port = 0
    if(headerLength==20):
        kind = int('0x' + message[32:34].decode("utf-8"),16)
        length = int('0x' + message[34:36].decode("utf-8"),16)
        port = int('0x' + message[36:40].decode("utf-8"),16)

    msgData = 0
    if(msgType == 'DATA'):
        data = message[32:]
        msgData = (binascii.unhexlify((data.encode()))).decode()

    return(sourcePort,destPort,seqNumber,ackNumber,msgType,rcvWndw,port,msgData)

def signal_handler(sig,frame):
    print("Received SIGINT...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    finPort = sock.getsockname()[1]
    sock.settimeout(60)

    for port in clientPort:
        finheader = create_fin(finPort,port,0,0)
        log(finPort,port, 'FIN', len(finheader))
        sock.sendto(bytes(finheader, 'utf-8'),(serverip,port))

        ack = 0
        ack, _ = sock.recvfrom(4096)
        if ack != 0:
            src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(ack)
        count = 1
        while (msgtype != 'ACK' and src != port and dest != finPort) or count != 3:
            sock.sendto(bytes(finheader, 'utf-8'),(serverip,port))
            ack, _ = sock.recvfrom(4096)
            if ack != 0:
                src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(ack)
            count+=1
    sock.close()
    welcomeSocket.close()
    sys.exit(0)

def accept(ip, srvport):
    signal.signal(signal.SIGINT, signal_handler)
    #open welcome socket at localhost:8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip,int(srvport)))
    print("Created Welcome Socket...")
    welcomeSocket = sock
    
    while True:
        #look for syn message
        print("Listening for SYN message...")
        syn, _ = sock.recvfrom(4096)
        #decode syn message
        src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(syn)
        if(msgtype == 'SYN'):
            #create a new server connection socket
            print("Creating Server Connect Socket...")
            connectsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #bind the server connection socket to a random port
            connectsock.bind(('', 0))
            #get the port number of the new connection socket so it can be sent back to client
            newPort = connectsock.getsockname()[1]
            #create a synack header (no need for message) with src = 8000, dest as newPort and seqnum = seqnum +1
            synackMsg = create_synack(srvport,src, str(int(seq) + 1),newPort)
            #send synack header to src of syn msg
            print("Sending SYN/ACK message...")
            log(srvport,src, 'SYN/ACK', len(synackMsg))
            sock.sendto(bytes(synackMsg, 'utf-8'), (ip, src))
            #wait for response ack message
            print("Waiting for ACK message...")
            ack, _ = sock.recvfrom(4096)
            #decode response ack message
            src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(ack)
            if port != 0:
                clientPort.append(port)
            #create a new thread with the server new connect socket and the port of the new client socket
            print("Starting Connection Thread...")
            thread = threading.Thread(target=connectionSocket, args=(connectsock,port,))
            #start the thread
            thread.start()

def connectionSocket(sock,clientPort):
    msgtype = 0
    connectServerPort = sock.getsockname()[1]
    while True:
        print("Waiting for ping...")
        recvmsg, _ = sock.recvfrom(4096)
        src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(recvmsg)
        if(msgtype == 'FIN'):
            break
        if(src == clientPort and dest == connectServerPort and msgtype == 'DATA'):
            message = create_datamessage(connectServerPort, src, ack, str(int(seq) + 4), 'pong')
            print("Sending pong...")
            log(connectServerPort,src, 'DATA', len(message))
            sock.sendto(bytes(message, 'utf-8'), (serverip, src))
    print("Received FIN message...")
    ackMsg = create_ack(dest,src,ack,seq)
    log(dest,src, 'ACK', len(ackMsg))
    print("Sending ACK message...")
    sock.sendto(bytes(ackMsg, 'utf-8'), (serverip,src))
    sock.close()

accept(serverip, serverport)

    

