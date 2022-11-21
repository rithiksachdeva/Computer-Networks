#Command: python3 senderSolano.py --dest_ip 127.0.0.1 --dest_port 8000 --input alice29.txt
import binascii
import threading
import random
import socket
from datetime import datetime
import sys
import signal
import random
import time
import os

serverip = sys.argv[2]
serverport = sys.argv[4]
serverConnectionPort = []
clientWelcomeSock = []
clientConnectionSock = []
inputfile = sys.argv[6]
sampleRTT = 0
EstimatedRTT = 0
DevRTT = 0
previousTimeout = 0

def timeout(resentFlag=0):
    global sampleRTT, EstimatedRTT, DevRTT, previousTimeout
    print("Sample RTT:",sampleRTT)
    if resentFlag == 1:
        timeoutInterval = previousTimeout * 2
        if timeoutInterval > 60:
            timeoutInterval = 60
        EstimatedRTT = 0
        DevRTT = 0
        return(timeoutInterval)
    else:
        if sampleRTT == 0 and previousTimeout == 0 and EstimatedRTT == 0 and DevRTT == 0:
            timeoutInterval = 1
            return(timeoutInterval)
        elif sampleRTT != 0 and EstimatedRTT == 0 and DevRTT == 0 and previousTimeout != 0 :
            EstimatedRTT = sampleRTT
            DevRTT = sampleRTT/2
            timeoutInterval = EstimatedRTT + (4 * DevRTT)
            if timeoutInterval < 1:
                timeoutInterval = 1
            return(timeoutInterval)
        else:
            EstimatedRTT = ((1 - 0.125) * EstimatedRTT) + (0.125 * sampleRTT)
            DevRTT = ((1-0.25) * DevRTT) + (0.25 * abs(sampleRTT - EstimatedRTT))
            timeoutInterval = EstimatedRTT + (4 * DevRTT)
            if timeoutInterval < 1:
                timeoutInterval = 1
            return(timeoutInterval)
def log(source,destination, messagetype, messagelength):
    dateTimeObj = datetime.now()
    currenttimestamp = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    logfile = open('log.txt', 'a')
    logfile.write(str(source) + " " + str(destination) + " " + str(messagetype) + " " + str(messagelength) + " " + currenttimestamp + "\n")
    logfile.close()

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

    #print(threading.get_native_id(), "Decoded message...", msgType, sourcePort, destPort, seqNumber, ackNumber, port, msgData)
    return(sourcePort,destPort,seqNumber,ackNumber,msgType,rcvWndw,port,msgData)


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
    print("HEADER SIZE",len(header))
    print("MESSAGE HEADER SIZE", len((binascii.hexlify(data)).decode()))
    message = header +(binascii.hexlify(data)).decode('utf-8')
    return(message)

def connect(ip,srvport):
    global sampleRTT,previousTimeout
    #Create Client Socket with random port
    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    welcomeSock.bind(('', 0))
    clientWelcomeSock.append(welcomeSock)
    print(threading.get_native_id(), "Created Client Welcome Socket...")
    signal.signal(signal.SIGINT, signal_handler)
    clientPort = welcomeSock.getsockname()[1]
    #create syn header (no need for message with syn) with random seqnum
    synMsg = create_syn(clientPort,srvport)
    synMsg = bytes(synMsg, 'utf-8')
    #decode the header created so we can keep the sequence number
    synsrc,syndest,synseq,synack,synmsgtype,synrcvwnd,synport, syndata = decode_message(synMsg)
    #send syn message to port 8000, which is where server is initialized
    print(threading.get_native_id(), "Sending SYN Message...")
    log(clientPort,srvport, 'SYN', len(synMsg))
    welcomeSock.sendto(synMsg, (ip,int(srvport)))
    #wait to receive synack message
    print(threading.get_native_id(), "Waiting for SYN/ACK message...")
    synackData, _ = welcomeSock.recvfrom(4096)
    #decode synack message and check that its seqnum + 1
    src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(synackData)
    print(threading.get_native_id(), "Serverport " + str(port))
    serverConnectionPort.append(port)
    print(threading.get_native_id(), "Serverport " + str(serverConnectionPort[0]))
    if(ack == int(synseq) + 1):
        print(threading.get_native_id(), "Created Client Connection Port...")
        connectionSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connectionSock.bind(('', 0))
        clientNewPort = connectionSock.getsockname()[1]
        clientConnectionSock.append(connectionSock)
        
        #create ack message with new connection ports: src = new client port, dest = new server port
        #change acknum to acknum + 1
        ackMsg = create_ack(clientPort,src,ack,str(int(seq) + 1),clientNewPort)
        #send ack message to the server welcome port, and then close this client port
        print(threading.get_native_id(), "Sending ACK message...")
        log(clientPort,src, 'ACK', len(ackMsg))
        welcomeSock.sendto(bytes(ackMsg, 'utf-8'),(ip,src))
        print(threading.get_native_id(), "Closing Client Welcome Socket...")
        welcomeSock.close()
        clientWelcomeSock[0] = 0

        #START HERE THE SENDING OF BYTES
        startTransfer = time.time()
        totalData = 0
        packetsSent = 0
        packetsLost = 0
        file = open(inputfile,'rb')
        packetSize = 1000
        fileoffsetAck = ack
        filesize = os.stat(inputfile).st_size

        resendFlag = 0
        while True:
            file.seek(ack-fileoffsetAck)
            data = file.read(packetSize - 16)
            if len(data) == 0:
                print("FINISHED DATA")
                break
            message = create_datamessage(clientNewPort,port,ack,str(int(seq) + 1),data)
            totalData = totalData + (len(message)/2)
            log(clientNewPort,port, 'DATA',len(message)/2)
            print("SENT NEW PACKET",clientNewPort,port,ack,seq, file.tell())
            previousTimeout = timeout(resendFlag)
            print("SET TIMEOUT", previousTimeout)
            startRTT = time.time()
            packetsSent += 1
            connectionSock.sendto(bytes(message, 'utf-8'),(ip,port))
            connectionSock.settimeout(previousTimeout)
            recvmsg = 0
            while(recvmsg == 0):
                try:
                    recvmsg,_ = connectionSock.recvfrom(4096)
                    endRTT = time.time()
                    if resendFlag == 0:
                        sampleRTT = endRTT - startRTT
                    resendFlag = 0
                except socket.error as e:
                    packetsLost += 1
                    print("TIMED OUT",e, type(e))
                    resendFlag = 1
                    print("RESENDING PACKET", clientNewPort,port,ack,seq)
                    break
            if resendFlag == 1:
                continue
            port,clientNewPort,seq,ack,msgtype,_,_,_ = decode_message(recvmsg)
            if msgtype == 'FIN':
                break
            print("RECV ACK PACKET",port,clientNewPort,seq,ack)
            
        if msgtype == 'FIN':
            ackMsg = create_ack(clientNewPort,port,ack,seq)
            log(clientNewPort,port, 'ACK', len(ackMsg))
            connectionSock.sendto(bytes(ackMsg, 'utf-8'), (ip, port))
        else:
            print("SENDING FIN")
            finheader = create_fin(clientNewPort,port,0,0)
            log(clientNewPort,port,'FIN',len(finheader))
            connectionSock.sendto(bytes(finheader, 'utf-8'), (ip,port))
            
            ack, _ = connectionSock.recvfrom(4096)
            src1,dest1,seq1,ack1,msgtype1,rcvwnd1,_,data1 = decode_message(ack)
            count = 1
            while (msgtype != 'ACK' and src1 != port and dest1 != clientNewPort) and count != 3:
                log(clientNewPort,port, 'FIN', len(finheader))
                connectionSock.sendto(bytes(finheader, 'utf-8'),(ip,port))
                ack, _ = connectionSock.recvfrom(4096)
                src1,dest1,seq1,ack1,msgtype1,rcvwnd1,_,data1 = decode_message(ack)
                count+=1
        connectionSock.close()
        file.close()
        endTransfer = time.time()
        print("TOTAL TIME TAKEN:", endTransfer-startTransfer)
        print("TOTAL BYTES TRANSFERRED", totalData + 16)
        print("PACKETS SENT/LOST:", packetsSent + 1, packetsLost)

def signal_handler(sig,frame):
    print(threading.get_native_id(), "Received SIGINT...")
    if(clientConnectionSock[0] != "" and serverConnectionPort[0] != ""):
        finPort = clientConnectionSock[0].getsockname()[1]
        clientConnectionSock[0].settimeout(15)

        finheader = create_fin(finPort,serverConnectionPort[0],0,0)
        log(finPort,serverConnectionPort[0], 'FIN', len(finheader))
        print(threading.get_native_id(), "Sent FIN...")
        clientConnectionSock[0].sendto(bytes(finheader, 'utf-8'),(serverip,serverConnectionPort[0]))

        print(threading.get_native_id(), "Looking for ACK...")
        ack, _ = clientConnectionSock[0].recvfrom(4096)
        src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(ack)
        print(threading.get_native_id(), "Received "  + msgtype + "...")
        print(threading.get_native_id(), src, serverConnectionPort[0], dest, finPort)
        count = 1
        while (msgtype != 'ACK' and src != serverConnectionPort[0] and dest != finPort) and count != 3:
            log(finPort,serverConnectionPort[0], 'FIN', len(finheader))
            clientConnectionSock[0].sendto(bytes(finheader, 'utf-8'),(serverip,serverConnectionPort[0]))
            ack, _ = clientConnectionSock[0].recvfrom(4096)
            src,dest,seq,ack,msgtype,rcvwnd,port,data = decode_message(ack)
            count+=1
        clientConnectionSock[0].close()
    if(clientWelcomeSock[0] != 0):
        clientWelcomeSock[0].close()
    
    sys.exit(0)
    
connect(serverip,serverport)
