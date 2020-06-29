from cryptography.fernet import Fernet
import os

os.chdir(r"C:\Users\samue\OneDrive\Documenti\Coding\Python\KeyLogger-2.0\testing")

key = "3F5_MIT38NjguwKLSztfCdeoOYPOMi3NKK0rEGCrlSg="
logfile = "log.txt"
newfile = "log-t.txt"

f = Fernet(key)
a = open(newfile, "a")

for i in open(logfile, "rb"):

    try:
        x = f.decrypt(i)
        message = x.decode()
        a.write(message)
        a.write("\n")
        print("Correct decrypt")
    except Exception as e:
        print("Error: " + e)
