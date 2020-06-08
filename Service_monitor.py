# coding: utf-8

import time
import subprocess
import os
import psutil
import platform
import threading
import cryptography
import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC



platform.system()
platform.release()
from sys import platform as _platform



#       Windows part #
##############################################

class WinService(threading.Thread):
    servicelog = []
    servicelogNew = []


    def __init__(self):
        threading.Thread.__init__(self)
        servs = psutil.win_service_iter()
        self.key = key_from_password()
        self.Status_Log_FileName="service_log" + ".txt"
        self.serviceList_Log_FileName = "serviceList" + ".txt"
        self.Status_Log = open(self.Status_Log_FileName,"a")
        self.serviceList = open(self.serviceList_Log_FileName, "a")
        self.sleep=0
        if  os.path.getsize(self.Status_Log_FileName)==0:
            self.Status_Log.write("Time,Service_Neame,Event\n")
            self.Status_Log.close()
        if os.path.getsize(self.serviceList_Log_FileName) == 0:
            self.serviceList.write("Time,Service_Neame,Event\n")
            self.serviceList.close()
        for serv in servs:
            self.servicelog.append(serv.display_name() + "," + serv.status())


    def getNewsServices(self):
        self.serviceList = open(self.serviceList_Log_FileName, 'a')
        self.servicelogNew.clear()
        servs = psutil.win_service_iter()
        for serv in servs:
            line = serv.display_name() + "," + serv.status()
            self.servicelogNew.append(line)
            message = time.ctime() + "," + line + "\n"
            encypted = encrypt(self.key, message)
            self.serviceList.write(encypted)
        self.serviceList.close()




    def serviceExist(self):

        for servlist in self.servicelog:
            exist = 0
            for listNew in self.servicelogNew:
                if (listNew == servlist):
                    exist = 1
                    break
            if exist == 0:
                self.Status_Log = open(self.Status_Log_FileName, 'a')
                message = time.ctime() + "," + servlist
                encypted = encrypt(self.key, message)
                #print(messege)
                self.Status_Log.write(encypted)
                self.servicelog.remove(servlist)
                self.Status_Log.close()

    def serviceNewExist(self):
        for listNew in self.servicelogNew:
            exist = 0
            for servlist in self.servicelog:
                if (listNew == servlist):
                    exist = 1
                    break
            if exist == 0:
                self.Status_Log = open(self.Status_Log_FileName, 'a')
                messege = time.ctime() +"," + listNew
                #print(messege)
                encypted = encrypt(self.key, messege)
                self.Status_Log.write(encypted)
                self.servicelog.append(listNew)
                self.Status_Log.close()


    def run(self):
        while (True):
                 self.getNewsServices()
                 self.serviceExist()
                 self.serviceNewExist()
                 time.sleep(self.sleep)



#       Linux part #
##############################################
class linux(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.historyLog = []
        self.key = key_from_password()
        self.Status_Log_FileName = "service_log" + ".txt"
        self.serviceList_Log_FileName = "serviceList" + ".txt"
        self.Status_Log = open(self.Status_Log_FileName, "a")
        self.serviceList=open(self.serviceList_Log_FileName, "a")
        self.sleep =0
        if  os.path.getsize(self.Status_Log_FileName)==0:
            self.Status_Log.write("Time,Service_Neame,Event\n")
            self.Status_Log.close()
        if os.path.getsize(self.serviceList_Log_FileName) == 0:
            self.serviceList.write("Time,Service_Neame,Event\n")
            self.serviceList.close()

    def monitor(self, newLog):
        # check if a sevice has died
        for history in self.historyLog:
            inside = 0
            for new in newLog:
                if (new != "" and history != "" and new in history):
                    inside = 1
            if inside == 0 and history != "":
                messege = time.ctime() + "," + history + ",changed status"
                #print(messege)
                self.Status_Log = open(self.Status_Log_FileName, 'a')
                encrypted = encrypt(self.key,messege)
                self.Status_Log.write(encrypted)
                self.Status_Log.close()



        # check if a service has born
        for new in newLog:
            inside = 0
            for history in self.historyLog:
                if (new != "" and history != "" and new in history):
                    inside = 1
            if inside == 0 and new != "":
                messege=time.ctime() + "," + new + ",changed status"
                #print(messege)
                self.Status_Log = open(self.Status_Log_FileName, 'a')
                encrypted = encrypt(self.key,messege)
                self.Status_Log.write(encrypted)
                self.Status_Log.close()



    def getNewLog(self):
        services = subprocess.check_output(["service", "--status-all"], universal_newlines=True)
        services = services.replace(" ", "")
        split = services.split("\n")
        return split

    def updateLog(self):
        self.serviceList = open(self.serviceList_Log_FileName, 'a')
        services = subprocess.check_output(["service", "--status-all"], universal_newlines=True)
        services = services.replace(" ", "")
        split = services.split("\n")
        self.historyLog = split
        for line in split:
            messege = time.ctime() + "," + line+"\n"
            ecncrypted = encrypt(self.key, messege)
            self.serviceList.write(ecncrypted)
        self.serviceList.close()

    def run(self):
        while (True):
                self.updateLog()
                time.sleep(self.sleep)
                self.monitor(self.getNewLog())



#       General  function  part #
##############################################


def getOs() :
    if _platform == "linux" or _platform == "linux2":
            return "linux"
    elif _platform == "win32" or _platform == "win64":
        return "win"
    else:
        return ""



def autoMonitor(sleepTime):

    os = getOs()


    if os == "linux":
            print("OS detected : linux\na"+time.ctime()+" starting automatic monitoring.")
            ubuntu = linux()
            ubuntu.sleep=sleepTime
            ubuntu.start()



    elif os=="win":
        print("OS detected : windows\n" + time.ctime()+ " starting automatic monitoring.")
        winServ = WinService()
        winServ.sleep=sleepTime
        winServ.start()


    else:
        print('your OS is unsupported at the moment  ')
        exit()


def menual():

    try:
        list =open("serviceList_decrypted.txt", 'r')
    except:
        print("no decrypted log files found first generate serviceList_decrypted.txt with the decrypt in menu ")
        return 
    print("please write first timestamp in this format (Month date hh:mm:ss year): ")
    firstMonth = input("Insert Mounth name (example May)")
    firstdate = input("Insert date name (example 01)")
    firsthour = input("Insert hh name (example 10)")
    firstminut = input("Insert mm name (example 12)")
    firstsecond = input("Insert ss name (example 55)")
    firstyear = input("Insert year name (example 2020)")
    firstTimestamp=firstMonth+" "+firstdate+" "+firsthour+":"+firstminut+":"+firstsecond+" "+firstyear
    print("please write second timestamp in this format (Month date hh:mm:ss year): ")
    secondMonth = input("Insert Mounth name (example May)")
    seconddate = input("Insert date name (example 01)")
    secondhour = input("Insert hh name (example 10)")
    secondminut = input("Insert mm name (example 12)")
    secondsecond = input("Insert ss name (example 55)")
    secondyear = input("Insert year name (example 2020)")
    secondTimestamp=secondMonth+" "+seconddate+" "+secondhour+":"+secondminut+":"+secondsecond+" "+secondyear


    firstLog=[]
    secondLog=[]
    for line in list:
        if line.__contains__(firstTimestamp):
            firstLog.append(line)
        elif line.__contains__(secondTimestamp):
            secondLog.append(line)

    for history in firstLog:
        inside = 0
        history=substringComa(history)
        for new in secondLog:
            if new =="" or history=="":
                continue
            new = substringComa(new)
            if (new != "" and history != "" and new in history):
                inside = 1
        if inside == 0 and history != "":
            messege = history + ",changed status\n"
            #print(messege)


        # check if a service has born
    for new in secondLog:
        inside = 0
        new =substringComa(new)
        for history in firstLog:
            history =substringComa(history)
            if (new != "" and history != "" and new in history):
                inside = 1
        if inside == 0 and new != "":
            messege = new + ",changed status\n"
            #print(messege)


def substringComa(word):
    wordStr=str(word)
    firstComaIndex = wordStr.find(',')
    wordStr=wordStr[firstComaIndex:]
    return wordStr



#       crypto  function  part #
##############################################

# with the help of this site
#https://nitratine.net/blog/post/encryption-and-decryption-in-python/
def key_from_password():
    password_provided = input("\n\nType a password :\n\n")
    password = password_provided.encode()  # Convert to type bytes
    salt = b'salt_'  # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
    return key


def decrypt_csv(key,input_file):

    try:

        output_file = str(input_file)
        output_file= output_file[0:output_file.find('.')]
        output_file+="_decrypted.txt"
        fernet = Fernet(key)
        out=open(output_file, 'a')

        first = True
        with open(input_file, 'r') as f:
                if first:
                    f.readline()
                    first=False
                for line in f:
                    data = f.readline()
                    line_byte = line.encode("utf-8")
                    line_byte=line_byte[2:-2]
                    decrypted = fernet.decrypt(line_byte)
                    decrypted_str = str(decrypted)
                    decrypted_str=decrypted_str[2:-2]
                    out.write(decrypted_str+"\n")
        out.flush()
        out.close()

    except:
        print("Eror during decryption , check your file name and password.")



def encrypt(key,message):
    str_message = str(message)
    f = Fernet(key)
    encrypted = f.encrypt(str_message.encode('utf-8'))
    encypted_str = str(encrypted)
    encypted_str +="\n"
    return encypted_str

def decrypt(key,encrypted):
    f = Fernet(key)
    decrypted = f.decrypt(encrypted)
    return decrypted
    
    
    
    
    
    
    
    

def main() :
    print("Service monitor created by Simon Pikalov")
    print("███████████████████████████████████\n███████████████████████████████████\n███████████████████████████████████\n█████████████▒▒▒▒▒▒▒▒▒█████████████\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█████████\n███████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒███████\n██████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██████\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█████\n█████▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒█████\n████▒▒▒▒███▒▒▒▒▒▒▒▒▒▒▒▒▒███▒▒▒▒████\n███▒▒▒▒██████▒▒▒▒▒▒▒▒▒██████▒▒▒▒███\n███▒▒▒███▐▀███▒▒▒▒▒▒▒███▀▌███▒▒▒███\n███▒▒▒██▄▐▌▄███▒▒▒▒▒███▄▐▌▄██▒▒▒███\n███▒▒▒▒██▌███▒▒▒█▒█▒▒▒███▐██▒▒▒▒███\n██▒▒▒▒▒▒███▒▒▒▒██▒██▒▒▒▒███▒▒▒▒▒▒██\n█▒▒▒▒▒▒▒▒█▒▒▒▒██▒▒▒██▒▒▒▒█▒▒▒▒▒▒▒▒█\n█▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒▒▒█\n█▒▒▒▒█▒▒█▒▒▒▒██▒▒▒▒▒██▒▒▒▒█▒▒█▒▒▒▒█\n██▒▒▒█▒▒█▒▒▒▒█▒██▒██▒█▒▒▒▒█▒▒█▒▒▒██\n███▒█▒▒█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒█▒███\n█████▒▒█▒▒▒▐███████████▌▒▒▒█▒▒█████\n███████▒▒▒▐█▀██▀███▀██▀█▌▒▒▒███████\n███████▒▒▒▒█▐██▐███▌██▌█▒▒▒▒███████\n███████▒▒▒▒▒▐▒▒▐▒▒▒▌▒▒▌▒▒▒▒▒███████\n████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒████████\n████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒████████\n█████████▒▒█▒█▒▒▒█▒▒▒█▒█▒▒█████████\n█████████▒██▒█▒▒▒█▒▒▒█▒██▒█████████\n██████████████▒▒███▒▒██████████████\n██████████████▒█████▒██████████████\n███████████████████████████████████\n███████████████████████████████████")
    isAutoRunning = False
    isManualRunning = False
    menuMessege = "please choose a action mode\nfor manual type manual , for automatic mode type auto and  to stop the program type stop or exit\ntype help to open the documentation "
    print(menuMessege)


    while(True):

        mode = input("\nchoose an action \n")

        if mode == "menual" or  mode == "m" :
                    menual()
                    print("Manual Mode ")
                    isManualRunning == True


        elif mode == "auto" or mode == "a" :
            if isAutoRunning == True:
                print("\nThe program is already running\n")

            else:
                sleepTime = input("\nchoose an Interval Time for the program in seconds:  \n")
                try:
                    val = float(sleepTime)
                    if val<0:
                        print("Not valid Input")
                    else:
                        autoMonitor(val)
                        isAutoRunning = True
                except ValueError:
                    print("Not valid Input")





        elif mode == "help" :

            print(
                "\n\n\n@author Simon Pikalov\nThis program helps monitor system services by whriting a log file that contain all the changes in the services on you machine.\n" + menuMessege)


        elif mode == "decrypt":
                key=key_from_password()
                file_name = input("To decrypt serviceList.txt type 1\nTo decrypt service_log.txt type 2\nTo decrypt other file type path to your file\n")
                if file_name in "1":
                    file_name = "serviceList.txt"
                elif file_name in "2":
                    file_name="service_log.txt"

                decrypt_csv(key,file_name)


        elif mode == "exit":
                exit()



main()
