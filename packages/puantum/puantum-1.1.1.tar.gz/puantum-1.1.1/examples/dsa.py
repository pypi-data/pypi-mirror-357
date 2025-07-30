# IMPORT
from puantum.quantum.dsa import Algorithm, KeyPair

# MAIN
alicesk, alicepk = KeyPair(Algorithm.MLDSA.MLDSA87)
message = "Hello".encode()

signature = alicesk.sign(message=message)
valid = alicepk.verify(signature=signature, message=message)

assert valid, "Signature verification failed!"

print(f"Message:   [{message.decode()}]")
print(f"Signature: [{signature.signature.hex()[:len(message)]}]")
