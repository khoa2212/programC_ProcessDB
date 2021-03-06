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
# Tr?????ng h???p ch??a n???m trong khung gi??? s??? d???ng ta s??? c?? hai c??ng vi???c sau

# H??m login cho ph??p l???y m???t kh???u nh???p t??? ng?????i d??ng v?? ki???m tra c?? l?? mk ph??? huynh
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

# H??m ki???m tra xem ????? 15s t??? l??c th??ng b??o hay ch??a
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
# Tr?????ng h???p n???m trong khung gi??? s??? d???ng ta s??? c?? c??c c??ng vi???c sau
# C??ng vi???c (a) C2.1.2.2
# ?????c th??ng tin t??? c?? s??? d??? li???u v?? th??ng b??o khung gi??? s??? d???ng
def printMessage():
    global StartTime
    global EndTime
    print('YOU ARE ACCEPTED USING COMPUTER FROM ' + datetime.strftime(StartTime, '%H:%M') +
          ' TO ' + datetime.strftime(EndTime, '%H:%M'))

# C??ng vi???c (b) C2.1.2.2
# T??nh to??n th???i gian v?? th??ng c??n bao nhi??u ph??t n???a s??? t???t v?? th???i gian ???????c b???t l???i
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

# B???t s??? ki???n b??n ph??m
def on_press(key):
    global inputString
    inputString = inputString + str(key) + ', '

# ?????y n???i dung DataKeyBoard.txt t??? m??y l??n cloud dropbox
def writeCharacterToFile(inputTime, inputDay, keyboardString):
    f = open('DataKeyBoard.txt', 'a') #ghi ??? ch??? ????? write append
    f.write('Day: ' + str(inputDay) + ' Time: ' + inputTime + ' KeyBoard: ' + str(keyboardString.encode('utf-8')) + '\n')
    Token = 'nEOBTK1z9mcAAAAAAAAAAXzcjPzI335QoeU3smHTig80igxXAIN3nRFnixwGqDUI'
    f.close()
    if os.stat("DataKeyBoard.txt").st_size != 0:
        dbx = dropbox.Dropbox(Token)
        with open('DataKeyBoard.txt', 'rb') as file:
            dbx.files_upload(file.read(), '/upload.txt', mode=WriteMode('overwrite'))

# Ghi n???i dung ph??m g?? xu???ng file c??ng v???i ???? l?? th???i gian v?? ng??y g??
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

# c???p nh???t s??? thay ?????i ??? c??c ??i???m th???i gian sau ???? th??ng b??o ra m??n h??nh
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

# ki???m tra s???p k???t th??c th???i gian d??ng m??y hay ch??a, c??n 1 ph??t th?? th??ng b??o, 0 ph??t th?? t???t m??y
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

    CheckPass = getPassword(Pass, ParentsPass) # L???y m???t kh???u t??? b??n ph??m
    if CheckPass:
        # L?? m???t kh???u ph??? huynh
        while True:
            time.sleep(3600)  # ?????i 60 ph??t sau ???? quay l???i b?????c C0 h???i m???t kh???u (b?????c C1)
            verifyPass = verifyPassParent(Pass, ParentsPass)
            if not verifyPass:
                # Nh???p sai m???t kh???u ph??? huynh 3 l???n th?? kh??a ph??m, chu???t ?????i 10 ph??t t???t m??y
                print('LOCK MOUSE')
                print('LOCK KEYBOARD')
                windll.user32.BlockInput(True)  # enable block
                time.sleep(600)
                windll.user32.BlockInput(False)  # disable block
                print('SHUT DOWN')
                os.system("shutdown /s /t 1")
                exit(0)
    else:
        # Kh??ng l?? m???t kh???u ph??? huynh
        checkT = checkTime(StartTime, EndTime, current_time) # Ki???m tra th???i gian c?? trong khung gi??? cho ph??p
        if checkT: # ???????c s??? d???ng m??y C2.1.2
            verifyPass = verifyPassChildren(Pass, ChildrenPass) #C2.1.2.1 ki??m tra xem c?? l?? m???t kh???u tr???
            if not verifyPass:
                # Nh???p sai 3 l???n v?? kh??ng d??ng ???????c m??y sau ???? kh??a b??n ph??m v?? chu???t ?????i 10 ph??t r???i t??t m??y
                print('LOCK MOUSE')
                print('LOCK KEYBOARD')
                windll.user32.BlockInput(True)  # enable block
                time.sleep(600)
                windll.user32.BlockInput(False)  # disable block
                print('SHUT DOWN')
                os.system("shutdown /s /t 1")
            else:
                # Nh???p ????ng m???t kh???u tr??? th?? th???c hi???n c??ng vi???c sau
                # L???y d??? li???u th??ng b??o kho???ng th???i gian s??? d???ng
                printMessage()
                # ????a ra th??ng b??o c??n bao nhi??u ph??t th?? k???t th??c v?? th???i gian ti???p theo b???t l??n
                caculateTime()
                # Th???c hi???n song song 3 c??ng vi???c
                while True:
                    p1 = threading.Thread(target=saveKeyboardhit)
                    p2 = threading.Thread(target=checkData())
                    p3 = threading.Thread(target=isFinish())
                    p1.start()
                    p2.start()
                    p3.start()
                    time.sleep(60) # sau m???i ph??t th?? quay l???i th???c hi???n 3 c??ng vi???c
        else: # kh??ng ???????c s??? d???ng m??y C2.1.1
            print('YOU ARE ACCEPTED USING COMPUTER FROM ' + datetime.strftime(StartTime, '%H:%M') + ' TO ' + datetime.strftime(EndTime, '%H:%M'))
            # Ch???y song song hai c??ng vi???c: ki???m tra 15s v?? nh???p m???t kh???u ph??? huynh ????ng l??c th?? d???ng t???t m??y
            process1 = threading.Thread(target=countTime)
            process2 = threading.Thread(target=Login(Pass, ParentsPass))
            process1.start()
            process2.start()
            if StopThread: # Bi???n to??n c???c ????? d???ng ti???n tr??nh ki???m tra 15s sau ???? t???t m??y
                while True:
                    time.sleep(3600)  # ?????i 60 ph??t sau ???? quay l???i b?????c C0 h???i m???t kh???u (b?????c C1)
                    verifyPass = verifyPassParent(Pass, ParentsPass)
                    if not verifyPass:
                        # Nh???p sai m???t kh???u ph??? huynh 3 l???n th?? kh??a ph??m, chu???t ?????i 10 ph??t t???t m??y
                        print('LOCK MOUSE')
                        print('LOCK KEYBOARD')
                        windll.user32.BlockInput(True)  # enable block
                        time.sleep(600)
                        windll.user32.BlockInput(False)  # disable block
                        print('SHUT DOWN')
                        os.system("shutdown /s /t 1")
                        exit(0)