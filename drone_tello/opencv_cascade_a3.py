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

host = ''
port = 9000
locaddr = (host,port)
i = 0 #画像保存カウント用
j = 0
start_bu = False
photo_t = True
is_running = True
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
    global is_running
    while is_running:
        try:
            data, server = sock.recvfrom(1518)
            tello_reply = data.decode(encoding="utf-8")
            print("tello:",tello_reply)
        except Exception:
            print ('\nExit . . .\n')
            break
        
def movie_save():
    global i
    global j
    global start_bu
    global photo_t
    global is_running
    sock.sendto(b'command', tello_address)
    print('command ok')
    time.sleep(0.5)
    sock.sendto(b'streamon', tello_address)
    print('stream on')
    cap = cv2.VideoCapture("udp://%s:%s?overrun_nonfatal=1&fifo_size=50000000" % ('192.168.11.7', '11111'))
    # cap = cv2.VideoCapture("udp:0.0.0.0:11111")
    print('start cap , button ok')
    while is_running:
        try:
            ret,frame = cap.read() # 今の映像を取得
            if ret:
                if start_bu ==True: # 画像認識飛行を押した時に以下のループに入る
                    if photo_t ==True: # 写真を保存した後、映像分析が終わるまでストップする                                          
                        j+=1 
                        if j ==200:
                            print('take photo now')
                            cv2.imwrite("img/img_" + str(i) + ".jpg",cv2.resize(frame, (500, 300))) # その画像を保存
                            photo_t =False
                            re = scan_sub() #保存した画像を解析して結果行動する
                            if re =="human":
                                cap.release()
                                endsys()
                                break
        except KeyboardInterrupt:
            sock.close()
            cv2.destroyAllWindows()
            cap.release()
            print('\nExit . . .\n')
            break
        
def scan_sub(): # scan_dataの中に解析結果を入れる
    global start_bu
    global photo_t
    global i
    global j
    print("tello idling")
    sock.sendto(b'command', tello_address)
    time.sleep(1)
  
    img = cv2.imread("img/img_" + str(i) + ".jpg")          
    grayimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                
    custom_cascade = cv2.CascadeClassifier('opencv_cascade/img_xml/haarcascade_frontalface_default.xml')               
    custom_rect = custom_cascade.detectMultiScale(grayimg,scaleFactor=1.1, minNeighbors=2,minSize=(50, 50))
           
    if len(custom_rect) >0:
        scan_data = "human"
    else:
        scan_data ="no"
    print("Cascade:",scan_data)
    
    if scan_data == 'human':#着地してシステム終了
        print("Get human face,land")
        sock.sendto(b'command', tello_address)
        time.sleep(1)
        sock.sendto(b'land',tello_address)
        time.sleep(5)
        human_image =cv2.imread("img/img_" + str(i) + ".jpg")
        for rect in custom_rect:
            cv2.rectangle(human_image, tuple(rect[0:2]), tuple(rect[0:2]+rect[2:4]), (0, 0, 255), thickness=3)
        cv2.imshow("get human face photo,wait for time",human_image)
        cv2.imwrite("img/img_last.jpg",human_image)
        cv2.waitKey(4000)
        return "human"

    else:# 顔意外の時は右にずれる
        print("No human face,right 40")
        sock.sendto(b'command', tello_address)
        time.sleep(1)
        sock.sendto(b'right 40',tello_address)
        time.sleep(2)
        photo_t = True
        i+=1  
        j = 0
        print('next scan')

    
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
    global is_running
    is_running = False
    sock.close()
    print("endsys:終了します")
    root.destroy()
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
