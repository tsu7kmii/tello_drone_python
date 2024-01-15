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
i = 0 #画像保存カウント用
start_bu = False
photo_t = True
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
    while True:
        try:
            data, server = sock.recvfrom(1518)
            tello_reply = data.decode(encoding="utf-8")
            print("tello:",tello_reply)
        except Exception:
            print ('\nExit . . .\n')
            break
        
def movie_save():
    global i
    global start_bu
    global photo_t
    j = 0
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'streamon', tello_address)
    print('send streamon > tello')
    cap = cv2.VideoCapture("udp://%s:%s?overrun_nonfatal=1&fifo_size=50000000" % ('192.168.11.7', '11111'))
    # cap = cv2.VideoCapture("udp:0.0.0.0:11111")
    print('start cap , button ok')
    while True:
        try:
            ret,frame = cap.read() # 今の映像を取得
            if ret:
                if start_bu ==True:
                    if photo_t ==True:                                         
                        j+=1 
                        if j ==200:
                            print('take photo now')
                            cv2.imwrite("img/img_" + str(i) + ".jpg",cv2.resize(frame, (500, 300))) # その画像を保存
                            photo_t =False
                            send_return = send_image() #保存した画像を桜鯖に投げて解析して結果行動する
                            j = 0
                            if send_return =="apple":
                                cap.release()
                                time.sleep(2)
                                endsys()
                                break
        except KeyboardInterrupt:
            sock.close()
            cv2.destroyAllWindows()
            cap.release()
            print('\nExit . . .\n')
            break
    
def send_image():
    global i
    try:
        print('send openai api image')
        scan_return = scan_sub()
        i+=1
        return scan_return
    except Exception:
        print("エラー")
        
def scan_sub(): # scan_dataの中に解析結果を入れる
    global start_bu
    global photo_t
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    scan_data = openai_api_analysis.image_gpt() 
    print("GPT:",scan_data)
    if scan_data == 'apple':#着地してシステム終了
        print("Get apple,land")
        sock.sendto(b'command', tello_address)
        time.sleep(1)
        sock.sendto(b'land',tello_address)
        time.sleep(5)
        apple_image =cv2.imread("img/img_" + str(i) + ".jpg")
        cv2.imshow("get apple photo,wait time",apple_image)
        cv2.waitKey(4000)
        return "apple"
    else:# りんご意外の時は右にずれる
        print("No apple,right 40")
        sock.sendto(b'command', tello_address)
        time.sleep(1)
        sock.sendto(b'right 40',tello_address)
        time.sleep(3)
        photo_t = True
        print('next scan')
        return "next"
    
#↓ウィンドウ関連

#ボタンがクリックされたら実行→Enter押したときに実行


def button_click():
    input_value = input_box.get()
    msg = input_value
    print(msg)
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
def endsys():
    sock.close()
    time.sleep(2)
    cv2.destroyAllWindows()
    print("終了します")
    sys.exit(0)

def takeoff():
    print("takeoff button")
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'takeoff',tello_address)

def land():
    print("land button")
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'land',tello_address)
    sock.close()
    sys.exit(0)

def d_start():# 開始ボタン（離陸して画像認識開始）
    global start_bu
    print("start button")
    sock.sendto(b'command', tello_address)
    time.sleep(1)
    sock.sendto(b'takeoff', tello_address)
    time.sleep(2)
    start_bu = True
    
#ウィンドウの作成
yoko = "500"
tate = "400"
text = "tello : I using openai api and when I find an apple I land on it. you can end by click [着陸] !"
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
   
#ボタンの作成
button = tkinter.Button(text="実行",command=button_click)
button.place(x=270, y=198)

b_takeoff = tkinter.Button(text="離陸",command=takeoff)
b_takeoff.place(x=20, y=250)

b_land = tkinter.Button(text="着陸",command=land)
b_land.place(x=80, y=250)

d_start_b= tkinter.Button(text="画像認識飛行開始",command=d_start)
d_start_b.place(x=140, y=250)

#スレッドの作成
recvThread = threading.Thread(target=recv)
movieThread = threading.Thread(target=movie_save)
#recvThread.setDaemon(True)
recvThread.start()
movieThread.setDaemon(True)
movieThread.start()

#ウインドウの描画
root.mainloop()
