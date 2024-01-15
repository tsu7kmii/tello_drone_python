#
# Tello Python3 Control Demo 
#
# http://www.ryzerobotics.com/
#
# 1/1/2018

import socket
import time

host = ''
port = 9000
locaddr = (host,port) 


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
    while True: 
        try:
            data, server = sock.recvfrom(1518)
            print("tello:",data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break


#recvThread create
with open("./drone_tello/hanakawa/commandtest.txt", 'r') as f:
    command = f.read().split()
print(command)

while True: 
    try:
        # Send data
        for cmd in command:
            msg = cmd
            print(msg)
            msg = msg.encode(encoding="utf-8") 
            sent = sock.sendto(msg, tello_address)
            time.sleep(7)
            if cmd =="land":
                print ('...')
                sock.close()  
                break
                
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()  
        break