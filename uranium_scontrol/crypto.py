import base64

from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES


class Crypto:
    key: str

    def __init__(self, key: str):
        # 补足长度为16整数倍
        self.key = key
        if len(self.key) <= 16:
            while len(self.key) < 16:
                self.key += "0"
        elif 16 <= len(self.key) <= 32:
            while 16 <= len(self.key) < 32:
                self.key += "0"

    def encrypt(self, content: str) -> str:  # aes ecb pkcs5
        byte = content.encode("utf-8")
        aes = AES.new(key=self.key.encode("utf-8"), mode=AES.MODE_ECB)
        pad_pkcs7 = pad(byte, AES.block_size, style="pkcs7")
        encrypted = aes.encrypt(pad_pkcs7)
        base64ed = base64.encodebytes(encrypted)
        return base64ed.decode("utf-8").replace("\n", "")

    def decrypt(self, content: str) -> str:
        base64ed = base64.decodebytes(content.encode("utf-8"))
        w = self.key.encode("utf-8")
        d = base64ed
        n = AES.new(w, AES.MODE_ECB)
        m = unpad(n.decrypt(d), AES.block_size, style="pkcs7")
        d = m.decode("utf-8")
        return d
