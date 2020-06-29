from cryptography.fernet import Fernet
key = Fernet.generate_key()
print("Key: " + str(key)[1:])
