#This file was created by Rithik Sachdeva
import binascii
import random

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


header = create_synack(1234, 80, 24951)
print(header)
message = create_datamessage("ping",header)
print(message)
src,dest,seq,ack,msgtype,rcvwnd,data = decode_message(message)
print(src,dest,seq,ack,msgtype,rcvwnd,data)

    

