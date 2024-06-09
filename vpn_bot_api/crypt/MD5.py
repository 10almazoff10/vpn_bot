from hashlib import md5

class MD5:
    def __init__(self, data = "Hello, world!"):
        self.data = data
    def encrypt(self):
        self.data = md5(self.data.encode()).hexdigest()
        return self.data
    def decrypt(self, data):
        if md5(data.encode()).hexdigest() == self.data:
            return data
            del self.data
        else:
            return "Error"

