import hashlib
text = "hello"
text_bytes = text.encode()


print("sha384:", hashlib.sha384(text_bytes))




print("sha3_256:", hashlib.sha3_256(text_bytes).hexdigest())
print("sha256:", hashlib.sha256(text_bytes).hexdigest())
print("shake_128:",
hashlib.shake_128(text_bytes).hexdigest(16))
print("sha224:", hashlib.sha224(text_bytes).hexdigest())
print("sha1:", hashlib.sha1(text_bytes).hexdigest())
print("blake2s:", hashlib.blake2s(text_bytes).hexdigest())