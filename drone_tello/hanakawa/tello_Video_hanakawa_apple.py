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
import Img_kaiseki_noriko
import requests

host = ''
port = 9000
locaddr = (host,port)
flag = False

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
    count = 0

    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print ('\nExit . . .\n')
            break

def send_image():#桜鯖にとった写真を投げるだけscan_subを動かして判別させる
    
    psurl = 'https://tondabayashi.sakura.ne.jp/drone/img_stock.php'
    try:
        img_data = open('Img_01.jpg','rb')
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

    i=0
    while True:
        try:
            ret, frame = cap.read()
            if i % 200 == 0:
                Reload_Flag = send_image()#編集中
                if Reload_Flag == 1:
                    print("終了")
                    sock.sendto(b'land',tello_address)
                    break
            i+=1
            if ret:
                cv2.imshow('TelloCamera', cv2.resize(frame, (700, 400)))
                cv2.waitKey(1)
                cv2.imwrite('Img_01.jpg',frame)
        except KeyboardInterrupt:
            sock.close()
            cv2.destroyAllWindows()
            cap.release()
            print('\nExit . . .\n')
            break

def scan_sub(): #解析に投げてscan_detaに結果を入れてそれがリンゴならドローンに着地指示
                #これが動くのは def send_imageの時
    scan_data = Img_kaiseki_noriko.image_api('Img_01.jpg',2)#変更点画像ファイル名
    print(scan_data)
    if scan_data == 'リンゴ' or scan_data == 'りんご':
        sock.sendto(b'land',tello_address)
        return 1
    else:
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


#ウィンドウの作成
yoko = "700";
tate = "400";
text = "Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed?\r\n"
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




#スレッドの作成
recvThread = threading.Thread(target=recv)
movieThread = threading.Thread(target=movie_save)
#recvThread.setDaemon(True)
recvThread.start()
movieThread.setDaemon(True)
movieThread.start()

#ウインドウの描画
root.mainloop()
