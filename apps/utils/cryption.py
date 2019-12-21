import base64

from Crypto.Cipher import AES

# 用于加密和解密的 base62 字符串
bs62_key, bs62_num = 't3cWih7SDm0fnEKu9RITFQPYXk16CvUMzN5gOZpjoJbBAxeyVdlra82s4GwqHL', 199701051314
aes_key, aes_iv = "V8xBcvlILyCbO4A6", "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"  # aes加密使用秘钥(key为16倍数位，不相同)


# base62加密函数
def encode_bs62(num: int, addcrc=None) -> str:
    try:
        num = bs62_num * num + 1
        ret = ''
        crc = bs62_key[int(str(num)[-1]) * 6]
        while num != 0:
            ret = (bs62_key[num % 62]) + ret
            num = num // 62
        if addcrc:
            # 在末尾添加一位随机字符
            ret += crc
        return ret
    except Exception:
        return str(num)


# base62解密函数
def decode_bs62(st: str, addcrc=None):
    if isinstance(st, str):
        ret, mult = 0, 1
        if addcrc:
            # 去掉最末一位的随机字符
            st = st[:-1]
        for c in reversed(st):
            ret += mult * bs62_key.index(c)
            mult *= 62
        if (ret - 1) % bs62_num == 0:
            return (ret - 1) // bs62_num
    return ""


# AES加密类(使用base64编码)
class Prpcrypt(object):
    def __init__(self, aes_key, aes_iv):
        self.key = aes_key
        self.IV = aes_iv
        self.mode = AES.MODE_CBC

    # PKCS5Padding
    def __pad(self, text):
        """填充方式，加密内容必须为16字节的倍数，若不足则使用self.iv进行填充"""
        text_length = len(text)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def __unpad(self, text):
        return text[:-ord(text[-1:])]

    # 加密函数
    def encrypt(self, text):
        crypt_obj = AES.new(self.key.encode("utf-8"), self.mode, self.IV.encode("utf-8"))
        crypt_str = crypt_obj.encrypt(bytes(self.__pad(text), encoding="utf-8"))
        return base64.b64encode(crypt_str).decode("utf-8")

    # 解密函数
    def decrypt(self, text):
        decode = base64.b64decode(text)
        crypt_obj = AES.new(self.key.encode("utf-8"), self.mode, self.IV.encode("utf-8"))
        plain_text = self.__unpad(crypt_obj.decrypt(decode)).decode("utf-8")
        return plain_text


aes_encrypt = Prpcrypt(aes_key, aes_iv)
