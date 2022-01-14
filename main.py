import mysql.connector
import time
import os
from datetime import datetime, date
import threading
from pynput import keyboard
from threading import Thread
import dropbox
from dropbox.files import WriteMode
from ctypes import *

# mydb = mysql.connector.connect( # local host
#     host='localhost',
#     user='root',
#     password='andy9999',
#     port='3306',
#     database='DatabaseProcess'
# )

mydb = mysql.connector.connect( # database online
    host='b03csmxdmazgc2u6l278-mysql.services.clever-cloud.com',
    user='uqybhwjdqoxmmd01',
    password='VCk0HT6OfGDcn97M1u6e',
    port='3306',
    database='b03csmxdmazgc2u6l278'
)

mycusor = mydb.cursor()


def getPassword(Pass, ParentsPass):
    Pass = input('Enter your password: ')
    if Pass == ParentsPass:
        print('YOU ARE ACCEPTED USING COMPUTER')
        return True
    else:
        return False


def verifyPassParent(Pass, ParentsPass):
    count = 0
    Pass = input('Enter your password again to verify you are parents: ')
    if Pass != ParentsPass:
        while Pass != ParentsPass:
            print('Enter wrong password wait 3 second to enter again, enter max 3 times')
            count = count + 1
            if count == 3:
                return False
            time.sleep(3)
            Pass = input('Enter your password again to verify you are parents: ')
    print('YOU ARE ACCEPTED USING COMPUTER')
    return True


def getData():
    mycusor.execute('select ID, Time_format(StartTime, "%H:%i") , Time_format(EndTime, "%H:%i"), Time_format(StartTimeAgain, "%H:%i") from ManageTime')
    data = mycusor.fetchall()
    return data


def verifyPassChildren(Pass, ChildrenPass):
    count = 0
    Pass = input('Enter your password again to verify you are children: ')
    if Pass != ChildrenPass:
        while Pass != ChildrenPass:
            print('Enter wrong password wait 3 second to enter again, enter max 3 times')
            count = count + 1
            if count == 3:
                return False
            time.sleep(3)
            Pass = input('Enter your password again to verify you are children: ')
    return True


def checkTime(Start, End, current_Time):
    if current_Time >= Start and current_Time <= End:
        return True
    else:
        print('YOU CAN NOT USE COMPUTER AT THIS TIME')
        return False


#-----------------------------------------------------------------------
# Trường hợp chưa nằm trong khung giờ sử dụng ta sẽ có hai công việc sau

# Hàm login cho phép lấy mật khẩu nhập từ người dùng và kiểm tra có là mk phụ huynh
def Login(Pass, ParentsPass):
    global StopThread
    print('Enter Parents password to stop shutdown')
    CheckPass = getPassword(Pass, ParentsPass)
    if CheckPass == True:  # la mat khau phu huynh
        StopThread = True
    else:
        print('Enter wrong parent password, enter again, maximum 3 times')
        count = 0
        while count < 3:
            count = count + 1
            print('Enter Parents password to stop shutdown')
            CheckPass = getPassword(Pass, ParentsPass)
            if CheckPass == True:
                StopThread = True
                break

# Hàm kiểm tra xem đủ 15s từ lúc thông báo hay chưa
def countTime():
    count = 0
    while count <= 15:
        time.sleep(1)
        count = count + 1

    if not StopThread:
        print('SHUT DOWN')
        os.system("shutdown /s /t 1")
        exit(0)

#---------------------------------------------------------------
# Trường hợp nằm trong khung giờ sử dụng ta sẽ có các công việc sau
# Công việc (a) C2.1.2.2
# Đọc thông tin từ cơ sở dữ liệu và thông báo khung giờ sử dụng
def printMessage():
    global StartTime
    global EndTime
    print('YOU ARE ACCEPTED USING COMPUTER FROM ' + datetime.strftime(StartTime, '%H:%M') +
          ' TO ' + datetime.strftime(EndTime, '%H:%M'))

# Công việc (b) C2.1.2.2
# Tính toán thời gian và thông còn bao nhiêu phút nữa sẽ tắt và thời gian được bật lại
def caculateTime():
    global StartTime
    global EndTime
    global StartTimeAgain

    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_time = datetime.strptime(current_time, '%H:%M')
    distance = EndTime - current_time
    print('TIME LEFT: ' + str(distance.total_seconds() / 60))
    print('YOU CAN TURN ON COMPUTER AGAIN IN: ' + datetime.strftime(StartTimeAgain, '%H:%M'))

# Bắt sự kiện bàn phím
def on_press(key):
    global inputString
    inputString = inputString + str(key) + ', '

# Đẩy nội dung DataKeyBoard.txt từ máy lên cloud dropbox
def writeCharacterToFile(inputTime, inputDay, keyboardString):
    f = open('DataKeyBoard.txt', 'a') #ghi ở chế độ write append
    f.write('Day: ' + str(inputDay) + ' Time: ' + inputTime + ' KeyBoard: ' + str(keyboardString.encode('utf-8')) + '\n')
    Token = 'nEOBTK1z9mcAAAAAAAAAAXzcjPzI335QoeU3smHTig80igxXAIN3nRFnixwGqDUI'
    f.close()
    if os.stat("DataKeyBoard.txt").st_size != 0:
        dbx = dropbox.Dropbox(Token)
        with open('DataKeyBoard.txt', 'rb') as file:
            dbx.files_upload(file.read(), '/upload.txt', mode=WriteMode('overwrite'))

# Ghi nội dung phím gõ xuống file cùng với đó là thời gian và ngày gõ
def saveKeyboardhit():
    today = date.today()
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    with keyboard.Listener(on_press=on_press) as ls:
        def time_out(period_sec: int):
            global inputString
            time.sleep(period_sec)  # Listen to keyboard for period_sec seconds
            if inputString != '':
                writeCharacterToFile(str(today), current_time, inputString)
                inputString = ''
            ls.stop()
        Thread(target=time_out, args=(40.0,)).start()
        ls.join()

# cập nhật sự thay đổi ở các điểm thời gian sau đó thông báo ra màn hình
def checkData():
    global StartTime
    global EndTime
    global StartTimeAgain

    mydb.commit()
    data = getData()
    if StartTime != datetime.strptime(data[0][1], '%H:%M') or EndTime != datetime.strptime(data[0][2], '%H:%M') or StartTimeAgain != datetime.strptime(data[0][3], '%H:%M'):
        StartTime = datetime.strptime(data[0][1], '%H:%M')
        EndTime = datetime.strptime(data[0][2], '%H:%M')
        StartTimeAgain = datetime.strptime(data[0][3], '%H:%M')
        printMessage()
        caculateTime()

# kiểm tra sắp kết thúc thời gian dùng máy hay chưa, còn 1 phút thì thông báo, 0 phút thì tắt máy
def isFinish():
    global EndTime
    global StartTimeAgain

    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_time = datetime.strptime(current_time, '%H:%M')
    distance = EndTime - current_time
    distance = distance.total_seconds() / 60
    if distance <= 0:
        print('SHUT DOWN')
        os.system("shutdown /s /t 1")
        exit(0)
    elif distance <= 1:
        caculateTime()

if __name__ == '__main__':
    StopThread = False
    ChildrenPass = '123'
    ParentsPass = '1234'
    Pass = ''
    inputString = ''
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    data = getData()
    StartTime = data[0][1]
    EndTime = data[0][2]
    StartTimeAgain = data[0][3]
    current_time = datetime.strptime(current_time, '%H:%M')
    StartTime = datetime.strptime(StartTime, '%H:%M')
    EndTime = datetime.strptime(EndTime, '%H:%M')
    StartTimeAgain = datetime.strptime(StartTimeAgain, '%H:%M')

    CheckPass = getPassword(Pass, ParentsPass) # Lấy mật khẩu từ bàn phím
    if CheckPass:
        # Là mật khẩu phụ huynh
        while True:
            time.sleep(3600)  # Đợi 60 phút sau đó quay lại bước C0 hỏi mật khẩu (bước C1)
            verifyPass = verifyPassParent(Pass, ParentsPass)
            if not verifyPass:
                # Nhập sai mật khẩu phụ huynh 3 lần thì khóa phím, chuột đợi 10 phút tắt máy
                print('LOCK MOUSE')
                print('LOCK KEYBOARD')
                windll.user32.BlockInput(True)  # enable block
                time.sleep(600)
                windll.user32.BlockInput(False)  # disable block
                print('SHUT DOWN')
                os.system("shutdown /s /t 1")
                exit(0)
    else:
        # Không là mật khẩu phụ huynh
        checkT = checkTime(StartTime, EndTime, current_time) # Kiểm tra thời gian có trong khung giờ cho phép
        if checkT: # Được sử dụng máy C2.1.2
            verifyPass = verifyPassChildren(Pass, ChildrenPass) #C2.1.2.1 kiêm tra xem có là mật khẩu trẻ
            if not verifyPass:
                # Nhập sai 3 lần và không dùng được máy sau đó khóa bàn phím và chuột đợi 10 phút rồi tăt máy
                print('LOCK MOUSE')
                print('LOCK KEYBOARD')
                windll.user32.BlockInput(True)  # enable block
                time.sleep(600)
                windll.user32.BlockInput(False)  # disable block
                print('SHUT DOWN')
                os.system("shutdown /s /t 1")
            else:
                # Nhập đúng mật khẩu trẻ thì thực hiện công việc sau
                # Lấy dữ liệu thông báo khoảng thời gian sử dụng
                printMessage()
                # Đưa ra thông báo còn bao nhiêu phút thì kết thúc và thời gian tiếp theo bật lên
                caculateTime()
                # Thực hiện song song 3 công việc
                while True:
                    p1 = threading.Thread(target=saveKeyboardhit)
                    p2 = threading.Thread(target=checkData())
                    p3 = threading.Thread(target=isFinish())
                    p1.start()
                    p2.start()
                    p3.start()
                    time.sleep(60) # sau mỗi phút thì quay lại thực hiện 3 công việc
        else: # không được sử dụng máy C2.1.1
            print('YOU ARE ACCEPTED USING COMPUTER FROM ' + datetime.strftime(StartTime, '%H:%M') + ' TO ' + datetime.strftime(EndTime, '%H:%M'))
            # Chạy song song hai công việc: kiểm tra 15s và nhập mật khẩu phụ huynh đúng lúc thì dừng tắt máy
            process1 = threading.Thread(target=countTime)
            process2 = threading.Thread(target=Login(Pass, ParentsPass))
            process1.start()
            process2.start()
            if StopThread: # Biến toàn cục để dừng tiến trình kiểm tra 15s sau đó tắt máy
                while True:
                    time.sleep(3600)  # Đợi 60 phút sau đó quay lại bước C0 hỏi mật khẩu (bước C1)
                    verifyPass = verifyPassParent(Pass, ParentsPass)
                    if not verifyPass:
                        # Nhập sai mật khẩu phụ huynh 3 lần thì khóa phím, chuột đợi 10 phút tắt máy
                        print('LOCK MOUSE')
                        print('LOCK KEYBOARD')
                        windll.user32.BlockInput(True)  # enable block
                        time.sleep(600)
                        windll.user32.BlockInput(False)  # disable block
                        print('SHUT DOWN')
                        os.system("shutdown /s /t 1")
                        exit(0)