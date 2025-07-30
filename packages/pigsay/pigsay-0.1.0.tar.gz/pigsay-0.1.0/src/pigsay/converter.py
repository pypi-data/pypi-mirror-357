from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class PigConverter:
    PREFIX = "猪曰:"

    class AESCipher:
        def __init__(self, key: bytes, iv: bytes):
            self.key = key
            self.iv = iv

        def encrypt(self, plaintext: bytes) -> bytes:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            return cipher.encrypt(pad(plaintext, AES.block_size))

        def decrypt(self, ciphertext: bytes) -> bytes:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            return unpad(cipher.decrypt(ciphertext), AES.block_size)

    def __init__(self, key: bytes = b"IsThisR3CTF2025?", iv: bytes = b"\x00" * 16):
        self.aes = self.AESCipher(key, iv)
        self.pig_charset = "豨豝豵豟豮豛豱豯豥豜豠豧豷豭豲豘"
        self.hex_to_pig = {
            _chr: self.pig_charset[i] for i, _chr in enumerate("0123456789abcdef")
        }
        self.pig_to_hex = {v: k for k, v in self.hex_to_pig.items()}

    def bytes_to_pig(self, byte_data: bytes) -> str:
        return "".join(self.hex_to_pig[ch] for ch in byte_data.hex())

    def pig_to_bytes(self, pig_str: str) -> bytes:
        return bytes.fromhex("".join(self.pig_to_hex[ch] for ch in pig_str))

    def encrypt_string(self, plaintext: str) -> str:
        ciphertext = self.aes.encrypt(plaintext.encode("utf-8"))
        return self.PREFIX + self.bytes_to_pig(ciphertext)

    def decrypt_string(self, cipher_text: str) -> str:
        if not cipher_text.startswith(self.PREFIX):
            raise ValueError(
                f"Invalid ciphertext format, missing prefix '{self.PREFIX}'"
            )
        rain_body = cipher_text[len(self.PREFIX) :]
        ciphertext = self.pig_to_bytes(rain_body)
        return self.aes.decrypt(ciphertext).decode("utf-8")

    def encrypt_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, "rb") as f_in:
            raw_data = f_in.read()
        ciphertext = self.aes.encrypt(raw_data)
        cipher_rain = self.PREFIX + self.bytes_to_pig(ciphertext)
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(cipher_rain)

    def decrypt_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, "r", encoding="utf-8") as f_in:
            cipher_rain = f_in.read().strip()
        if not cipher_rain.startswith(self.PREFIX):
            raise ValueError(
                f"Invalid ciphertext format, missing prefix '{self.PREFIX}'"
            )
        ciphertext = self.pig_to_bytes(cipher_rain[len(self.PREFIX) :])
        raw_data = self.aes.decrypt(ciphertext)
        with open(output_path, "wb") as f_out:
            f_out.write(raw_data)
