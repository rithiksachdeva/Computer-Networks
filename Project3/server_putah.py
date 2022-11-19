#SERVER
import threading
import binascii
import random
import socket
import sys
from datetime import datetime
import signal
import os, os.path

serverip = sys.argv[2]
serverport = sys.argv[4]
clientPort = []
welcomeSocket = []
serverConnectionSocketsArray = []

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
        msgData = data.decode('utf-8')

    print(threading.get_native_id(), "Decoded message...", msgType, sourcePort, destPort, seqNumber, ackNumber, port, msgData)
    return(sourcePort,destPort,seqNumber,ackNumber,msgType,rcvWndw,port,msgData)


def accept(ip, srvport):
    #open welcome socket at localhost:8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip,int(srvport)))
    print(threading.get_native_id(), "Created Welcome Socket...")
    signal.signal(signal.SIGINT, signal_handler)
    welcomeSocket.append(sock)
    stop_event = threading.Event()
    if(os.path.exists('log.txt')):
        os.remove('log.txt')
    
    while welcomeSocket[0] != "":
        #look for syn message
        print(threading.get_native_id(), "Listening for SYN message...")
        try:
        	syn, _ = sock.recvfrom(4096)
        except socket.error as e:
        	#print (threading.get_native_id(), "Error creating socket: %s" % e) 
        	break
        #decode syn message
        src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(syn)
        if(msgtype == 'SYN'):
            #create a new server connection socket
            print(threading.get_native_id(), "Creating Server Connect Socket...")
            connectsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            connectsock.settimeout(10)
            #bind the server connection socket to a random port
            connectsock.bind(('', 0))
            #get the port number of the new connection socket so it can be sent back to client
            newPort = connectsock.getsockname()[1]
            #create a synack header (no need for message) with src = 8000, dest as newPort and seqnum = seqnum +1
            synackMsg = create_synack(srvport,src, str(int(seq) + 1),newPort)
            #send synack header to src of syn msg
            print(threading.get_native_id(), "Sending SYN/ACK message...")
            log(srvport,src, 'SYN/ACK', len(synackMsg))
            sock.sendto(bytes(synackMsg, 'utf-8'), (ip, src))
            #wait for response ack message
            print(threading.get_native_id(), "Waiting for ACK message...")
            ack, _ = sock.recvfrom(4096)
            #decode response ack message
            src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(ack)
            if port != 0:
                clientPort.append(port)
            #create a new thread with the server new connect socket and the port of the new client socket
            print(threading.get_native_id(), "Starting Connection Thread...")
            serverConnectionSocketsArray.append(connectsock)
            thread = threading.Thread(target=connectionSocket, args=(connectsock,port,stop_event,))
            #start the thread
            thread.start()
    stop_event.set()
    thread.join()

def connectionSocket(sock,clientPort1,stop_event):
    msgtype = 0
    connectServerPort = sock.getsockname()[1]
    print(threading.get_native_id(), "Ping/Pong begins...")
    while True:
        try:
            recvmsg, _ = sock.recvfrom(4096)
            print(threading.get_native_id(), stop_event.is_set())
            if stop_event.is_set():
                 msgtype = ""
                 break
        except socket.error as e:
            print("TIMED OUT")
            #print (threading.get_native_id(), "Error connection socket: %s" % e) 
            if stop_event.is_set():
                 msgtype = ""
                 break
            continue
        src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(recvmsg)
        if(msgtype == 'FIN'):
            print(threading.get_native_id(), "Received FIN message...")
            break
        if(src == clientPort1 and dest == connectServerPort and msgtype == 'DATA'):
            message = create_datamessage(connectServerPort, src, ack, str(int(seq) + 4), 'pong')
            log(connectServerPort,src, 'DATA', len(message))
            sock.sendto(bytes(message, 'utf-8'), (serverip, src))
    if(msgtype == ""):
        print(threading.get_native_id(), "Send FIN to...", port)
        finheader = create_fin(dest,src,0,0)
        log(dest,src,'FIN',len(finheader))
        sock.sendto(bytes(finheader, 'utf-8'), (serverip,src))      

        print(threading.get_native_id(), "Looking for ACK...")
        ack, _ = sock.recvfrom(4096)
        src1,dest1,seq1,ack1,msgtype1,rcvwnd1,_,data1 = decode_message(ack)
        print(threading.get_native_id(), "Received "  + msgtype1 + "...", src, src1, dest, dest1)
        count = 1
        while (msgtype != 'ACK' and src1 != src and dest1 != dest) and count != 3:
            print(threading.get_native_id(), "Resending FIN...")
            log(dest,src, 'FIN', len(finheader))
            sock.sendto(bytes(finheader, 'utf-8'),(serverip,src))
            ack, _ = sock.recvfrom(4096)
            src1,dest1,seq1,ack1,msgtype1,rcvwnd1,_,data1 = decode_message(ack)
            count+=1
    else:
        ackMsg = create_ack(dest,src,ack,seq)
        log(dest,src, 'ACK', len(ackMsg))
        print(threading.get_native_id(), "Sending ACK message...")
        sock.sendto(bytes(ackMsg, 'utf-8'), (serverip,src))
    clientPort.remove(src)
    print(threading.get_native_id(), "Closing Socket...")
    sock.close()
    serverConnectionSocketsArray.remove(sock)

def signal_handler(sig,frame):
    print(threading.get_native_id(), "Received SIGINT...")
    print("Closing Welcome socket...")
    welcomeSocket[0].close()
    print(threading.get_native_id(), "Signal exit....")

accept(serverip, serverport)
print(threading.get_native_id(), "Exiting...")
# wait for the all thread to stop
sys.exit(0)
