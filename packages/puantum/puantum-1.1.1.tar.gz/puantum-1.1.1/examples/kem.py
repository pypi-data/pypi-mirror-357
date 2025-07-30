# IMPORT
from puantum.quantum.kem import Algorithm, KeyPair

# MAIN
alicesk, alicepk = KeyPair(Algorithm.MLKEM.MLKEM1024)
_bobsk, _bobpk = KeyPair(Algorithm.MLKEM.MLKEM1024)

bobss, bobct = alicepk.encapsulate()
alicess = alicesk.decapsulate(bobct)

assert alicess.sharedsecret == bobss.sharedsecret, "Shared secrets do not match!"

print(f"Alice's Shared Secret: [{alicess.sharedsecret.hex()}]")
print(f"Bob's   Shared Secret: [{bobss.sharedsecret.hex()}]")
