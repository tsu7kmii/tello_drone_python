#
# Tello Python3 Control Demo
#
# http://www.ryzerobotics.com/
#
#coment:UTF-8
# 11/29/2023

import threading
import socket
import sys
import time
import tkinter
import cv2
import openai_api_analysis
import requests

host = ''
port = 9000
locaddr = (host,port)
flag = False
i = 0 #画像保存カウント用
start_bu = False
msgmsg = True
photo_t = True
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
    global msglist
    global msgmsg
    while True:
        try:
            data, server = sock.recvfrom(1518)
            tello_reply = data.decode(encoding="utf-8")
            print("tello:",tello_reply);msglist +='> tello:' +str(tello_reply)+'\n';msgmsg = True
        except Exception:
            print ('\nExit . . .\n')
            break
        
def movie_save():
    global i
    global msglist
    global msgmsg
    global start_bu
    global photo_t
    j = 100
    sock.sendto(b'command', tello_address)
    print('command ok');msglist +='> command ok \n';msgmsg = True
    time.sleep(0.5)
    sock.sendto(b'streamon', tello_address)
    print('stream on');msglist +='> stream on \n';msgmsg = True
    cap = cv2.VideoCapture("udp://%s:%s?overrun_nonfatal=1&fifo_size=50000000" % ('192.168.11.7', '11111'))
    # cap = cv2.VideoCapture("udp:0.0.0.0:11111")
    print('start cap , button ok');msglist +='> start cap , button ok \n';msgmsg = True
    while True:
        try:
            ret,frame = cap.read() # 今の映像を取得
            if ret:
                if start_bu ==True:
                    if photo_t ==True:                                         
                        j+=1 
                        if j ==200:
                            msglist +='> take photo now \n';msgmsg = True
                            cv2.imwrite("img/img_" + str(i) + ".jpg",cv2.resize(frame, (500, 300))) # その画像を保存
                            photo_t =False
                            send_image() #保存した画像を桜鯖に投げて解析して結果行動する
                            j = 0
                            
        except KeyboardInterrupt:
            sock.close()
            cv2.destroyAllWindows()
            cap.release()
            print('\nExit . . .\n')
            break
    
def send_image():
    global i
    global msglist
    global msgmsg
    psurl = 'https://tondabayashi.sakura.ne.jp/drone/img_stock.php'
    try:
        sock.sendto(b'command', tello_address)
        time.sleep(1)
        img_data = open("img/img_" + str(i) + ".jpg",'rb')
        requests.post(psurl,img_data)
        msglist +='> send php image \n';msgmsg = True     
        scan_sub()
        i+=1
    except Exception:
        print("エラー");msglist +='> send_image error \n';msgmsg = True 
        
def scan_sub(): # scan_dataの中に解析結果を入れる
    global msglist
    global msgmsg
    global start_bu
    global photo_t
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    scan_data = openai_api_analysis.image_gpt() 
    print("GPT:",scan_data)
    if scan_data == 'apple':#着地してシステム終了
        print("Get apple,land");msglist +='> Get apple,land \n';msgmsg = True
        sock.sendto(b'command', tello_address)
        time.sleep(1)
        sock.sendto(b'land',tello_address)
        time.sleep(10)
        print("終了します")
        sock.close()
        sys.exit(0)
    else:# りんご意外の時は右にずれる
        print("No apple,right 30");msglist +='> No apple,right 30 \n';msgmsg = True
        sock.sendto(b'command', tello_address)
        time.sleep(1)
        sock.sendto(b'right 40',tello_address)
        time.sleep(2)
        photo_t = True
        msglist +='> next scan \n';msgmsg = True
    
#↓ウィンドウ関連

#ボタンがクリックされたら実行→Enter押したときに実行
def button_click(self):
    global msg
    global msglist
    global msgmsg
    input_value = input_box.get()
    msg = input_value
    print(msg)
    sendlogmsg = '> ' + input_value +'\n'
    msglist += str(sendlogmsg);msgmsg = True
    try:
        if msg=="":
            time.sleep(2)
            sock.close()
            sys.exit(0)
        if 'end' in msg:
            print ('...')
            sock.close()
            sys.exit(0)
        # Send data
        msg = msg.encode(encoding="utf-8") 
        sent = sock.sendto(msg, tello_address)
        input_box.delete("0",tkinter.END)
    except KeyboardInterrupt:
        print ('\n . . .\n')
        sock.close()

#各ボタンが押されたらコマンドを送る処理
def takeoff():
    global msglist
    global msgmsg
    msglist += '> click takeoff buttun \n';msgmsg = True
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'takeoff',tello_address)

def land():
    global msglist
    global msgmsg
    msglist += '> click land buttun \n';msgmsg = True
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'land',tello_address)
    sock.close()
    sys.exit(0)

def d_start():# 開始ボタン（離陸して画像認識開始）
    global msglist
    global msgmsg
    global start_bu
    msglist += '> click start buttun \n';msgmsg = True
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'takeoff', tello_address)
    time.sleep(2)
    start_bu = True
    
#ウィンドウの作成
yoko = "700"
tate = "400"
text = "tello : I using openai api and when I find an apple I land on it. \r\n If you want to exit the system, type end and Enter !\n or you can end by click [着陸] !"
root = tkinter.Tk()

root.title("image recognition flight system")
root.geometry(yoko+"x"+tate)
iconfile = 'icon48.ico'
#root.iconbitmap(default=iconfile)

#入力欄の作成
input_box = tkinter.Entry(width=40)
input_box.place(x=10, y=200)
# input_box.bind('<Return>', button_click)

#ラベルの作成
input_label = tkinter.Label(text=text)
input_label.place(x=10, y=30)

msglist = ">> log messages \n"

def addlabel():
    global msglist
    global msgmsg
    while True:
        try:
            input_box.bind('<Return>', button_click) #inputboxのenterを拾って実行を押す,スレッドで動かす必要があるのでここで共同動作
            if msgmsg ==True:  
                scroll_Y = tkinter.Scrollbar( orient = 'vertical' )
                tex = tkinter.Text( background = '#DFDFFF', yscrollcommand = scroll_Y.set)
                tex.place( x = 400, y = 50, width = 220, height = 330 )
                scroll_Y[ 'command' ] = tex.yview
                scroll_Y.place( x = 620, y = 50, height = 330 )                              
                tex.insert(tkinter.END, msglist)
                msgmsg = False
        except Exception:
            print ('\nExit . . .\n')
            break
            
#ボタンの作成
# button = tkinter.Button(text="実行",command=button_click)
# button.place(x=270, y=198)

b_takeoff = tkinter.Button(text="離陸",command=takeoff)
b_takeoff.place(x=20, y=250)

b_land = tkinter.Button(text="着陸",command=land)
b_land.place(x=80, y=250)

d_start_b= tkinter.Button(text="画像認識飛行開始",command=d_start)
d_start_b.place(x=140, y=250)

#スレッドの作成
recvThread = threading.Thread(target=recv)
movieThread = threading.Thread(target=movie_save)
textThread = threading.Thread(target=addlabel)
#recvThread.setDaemon(True)
recvThread.start()
movieThread.setDaemon(True)
movieThread.start()
textThread.setDaemon(True)
textThread.start()

#ウインドウの描画
root.mainloop()
