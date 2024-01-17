#
# Tello Python3 Control Demo
#
# http://www.ryzerobotics.com/
#
#coment:UTF-8
# 1/1/2018

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

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

i = 0

def recv():
    count = 0

    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break

def send_image():
    psurl = 'https://tondabayashi.sakura.ne.jp/drone/img_stock.php'
    try:
        img_data = open("img/img_" + str(i) + ".jpg",'rb')
        requests.post(psurl,img_data)
        flag = scan_sub()
        return flag
    except Exception:
        print("エラー")

def movie_save():
    sock.sendto(b'command', tello_address)
    print('command ok')
    time.sleep(0.5)
    sock.sendto(b'streamon', tello_address)
    print('stream on')
    time.sleep(1)
    cap = cv2.VideoCapture("udp:0.0.0.0:11111")#"udp://%s:%s?overrun_nonfatal=1&fifo_size=50000000" % ('192.168.11.7', '11111'
    print('start cap')
    
    global i
    while True:
        try:
            ret, frame = cap.read()
            if i % 200 == 0:
                Reload_Flag = send_image()#編集中
                if Reload_Flag == 1: #たぶんいらん
                    print("終了")
                    sock.sendto(b'land',tello_address)
                    break
            if ret:
                if i % 200 == 0:
                    cv2.imshow('TelloCamera', cv2.resize(frame, (700, 400)))
                    cv2.waitKey(1)
                    cv2.imwrite("img/img_" + str(i) + ".jpg",frame)
            i+=1
        except KeyboardInterrupt:
            sock.close()
            cv2.destroyAllWindows()
            cap.release()
            print('\nExit . . .\n')
            break

def scan_sub(): # scan_dataの中に解析結果を入れる
    scan_data = openai_api_analysis.image_gpt(1) 
    print(scan_data)
    if scan_data == 'apple':
        sock.sendto(b'land',tello_address)
        return 1
    else:
        sock.sendto(b'right 30',tello_address)
        return 0
    

#ボタンがクリックされたら実行
def button_click():
    global msg
    global input_label
    input_value = input_box.get()
    msg = input_value
    input_label.place_forget()
    input_label = tkinter.Label(text=msg)
    input_label.place(x=10, y=70)
    print(msg)
    try:
        if msg=="":
            input_label.place_forget()
            input_label = tkinter.Label(text="コマンドが入力されていないため、システムを終了します。")
            input_label.place(x=10, y=70)
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
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'takeoff',tello_address)

def land():
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'land',tello_address)

def cw_360():
    # 時計回り
    sock.sendto(b'command',tello_address)
    time.sleep(1)
    sock.sendto(b'cw 360',tello_address)

def ccw_360():
    # 反時計
    sock.sendto(b'command',tello_address)
    time.sleep(1)
    sock.sendto(b'ccw 360',tello_address)

def forward_30():
    # 前進
    sock.sendto(b'command',tello_address)
    time.sleep(1)
    sock.sendto(b'forward 30',tello_address)
    
def back_30():
    # 後進
    sock.sendto(b'command',tello_address)
    time.sleep(1)
    sock.sendto(b'back 30',tello_address)

def s_move():
    # 四角移動
    sock.sendto(b'command',tello_address)
    time.sleep(1)
    sock.sendto(b'forward 30',tello_address)
    time.sleep(5)
    sock.sendto(b'left 30',tello_address)
    time.sleep(5)
    sock.sendto(b'back 30',tello_address)
    time.sleep(5)
    sock.sendto(b'right 30',tello_address)
    time.sleep(5)
    sock.sendto(b'forward 30',tello_address)


#ウィンドウの作成
yoko = "700";
tate = "400";
text = "Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n      if you finish send end\r\n"
root = tkinter.Tk()

root.title("画像認識飛行プログラム")
root.geometry(yoko+"x"+tate)
iconfile = 'icon48.ico'
#root.iconbitmap(default=iconfile)

#入力欄の作成
input_box = tkinter.Entry(width=40)
input_box.place(x=10, y=200)

#ラベルの作成
input_label = tkinter.Label(text=text)
input_label.place(x=10, y=70)


#ボタンの作成
button = tkinter.Button(text="実行",command=button_click)
button.place(x=10, y=130)

ririku = tkinter.Button(text="離陸",command=takeoff)
ririku.place(x=500, y=60)

chakuriku = tkinter.Button(text="着陸",command=land)
chakuriku.place(x=500, y=100)

hidari = tkinter.Button(text="左旋回",command=cw_360)
hidari.place(x=550, y=140)

migi = tkinter.Button(text="右旋回",command=ccw_360)
migi.place(x=550, y=180)

mae = tkinter.Button(text="前進",command=forward_30)
mae.place(x=550, y=60)

usiro = tkinter.Button(text="後進",command=back_30)
usiro.place(x=550, y=100)

smove = tkinter.Button(text="四角移動",command=s_move)
smove.place(x=450, y=160)

#スレッドの作成
recvThread = threading.Thread(target=recv)
movieThread = threading.Thread(target=movie_save)
#recvThread.setDaemon(True)
recvThread.start()
movieThread.setDaemon(True)
movieThread.start()

#ウインドウの描画
root.mainloop()
