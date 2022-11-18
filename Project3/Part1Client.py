#This file was created by Rithik Sachdeva
import binascii
import random
import socket
from datetime import datetime
import sys

serverip = sys.argv[2]
serverport = sys.argv[4]
destinationPortforSigint = ""

def log(source,destination, messagetype, messagelength):
    dateTimeObj = datetime.now()
    currenttimestamp = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    logfile = open('log.txt', w)
    logfile.write(source + " " + destination + " " + messagetype + " " + messagelength + " " + currenttimestamp)
    logfile.close()

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
    rcvWndw = int('0x' + rcvWnd,16)

    kind = 0
    length = 0
    port = 0
    if(headerLength==20):
        kind = int('0x' + message[32:34],16)
        length = int('0x' + message[34:36],16)
        port = int('0x' + message[36:40],16)

    msgData = 0
    if(msgType == 'DATA'):
        data = message[32:]
        msgData = (binascii.unhexlify((data.encode()))).decode()

    return(sourcePort,destPort,seqNumber,ackNumber,msgType,rcvWndw,port,msgData)

def signal_handler(sig,frame):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    finPort = sock.getsockname()[1]
    sock.settimeout(5)

    finheader = create_fin(finPort,destinationPortforSigint,0,0)
    log(finPort,destinationPortforSigint, 'FIN', len(finheader))
    sock.sendto(finheader,('127.0.0.1',destinationPortforSigint))
    ack, _ = sock.recvfrom(4096)
    src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(ack)
    count = 1
    while msgtype != 'ACK' or count != 3:
        sock.sendto(finheader,('127.0.0.1',port))
        ack, _ = sock.recvfrom(4096)
        src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(ack)
        count+=1

    sock.close()
    sys.exit(0)
        

def create_header(srcprt, destprt, seqnum, acknum, ack, syn, fin, optionLength=0):

    srcPort = "{:04x}".format(srcprt)
    destPort = "{:04x}".format(destprt)
    sequenceNum = "{:08x}".format(seqnum)
    headerNum = "{:08x}".format(acknum)

    
    headerLength = format(((16+optionLength) / 4),"b").zfill(4)
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

def create_syn(src,dest):
    seq = random.randint(20000,30000)
    header = create_header(src,dest,seq,0,0,1,0)
    return(header)
    
def create_ack(src,dest,seq,ack,port=0):
    if port != 0:
        header = create_header(src,dest,seq,ack,1,0,0,4)
        options = create_options(252,4, port)
        return(header + options)
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


def connect(ip,port):
    #Create Client Socket with random port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0))
    clientPort = sock.getsockname()[1]
    #create syn header (no need for message with syn) with random seqnum
    synMsg = create_syn(clientPort,port)
    #decode the header created so we can keep the sequence number
    synsrc,syndest,synseq,synack,synmsgtype,synrcvwnd,synport, syndata = decode_message(synMsg)
    #send syn message to port 8000, which is where server is initialized
    log(clientPort,port, 'SYN', len(synMsg))
    sock.sendto(synMsg, (ip,port))
    #wait to receive synack message
    synackData, _ = sock.recvfrom(4096)
    #decode synack message and check that its seqnum + 1
    src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(synackData)
    if(ack == str(int(synseq) + 1)):
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock1.bind(('', 0))
        clientNewPort = sock1.getsockname()[1]
        
        #create ack message with new connection ports: src = new client port, dest = new server port
        #change acknum to acknum + 1
        ackMsg = create_ack(clientPort,src,ack,str(int(seq) + 1),clientNewPort)
        #send ack message to the server welcome port, and then close this client port
        log(clientPort,src, 'ACK', len(ackMsg))
        sock.sendto(ackMsg,(ip,src))
        sock.close()

        #create new header for first ping message
        signal.signal(signal.SIGINT, signal_handler)
        destinationPortforSigint = dest
        header = create_datahdr(newClientConnection,dest,seq,str(int(ack) + 1))
        message = create_datamessage('ping',header)
        log(newClientConnection,dest, 'DATA', len(message))
        sock1.sendto(message, ('127.0.0.1', dest))
        while msgtype != 'FIN':
            recvmsg,_ = sock1.recvfrom(4096)
            src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(recvmsg)
            if(src == dest and msgtype == 'DATA'):
                destinationPortforSigint = src
                header = create_datahdr(dest,src,ack,str(int(seq) + 4))
                message = create_datamessage('ping',header)
                log(dest,src, 'DATA', len(message))
                sock1.sendto(message, ('127.0.0.1', src))
        
        ackMsg = create_ack(dest,src,seq,ack)
        log(dest,src, 'ACK', len(ackMsg))
        sock1.sendto(ackMsg, ('127.0.0.1', src))
        sock1.close()



   
       
    
    

