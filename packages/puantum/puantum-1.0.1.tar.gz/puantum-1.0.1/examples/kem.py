# IMPORT
from puantum.quantum.kem import Algorithm, KeyPair

# MAIN
def main():
    # Generate Alice's KEM keypair (secret and public keys)
    alicesk, alicepk = KeyPair(Algorithm.MLKEM.MLKEM1024)
    # Generate Bob's KEM keypair (optional here unless Bob also receives messages)
    _bobsk, _bobpk = KeyPair(Algorithm.MLKEM.MLKEM1024)
    # Bob uses Alice's public key to encapsulate a shared secret and a ciphertext
    bob_shared_secret, ciphertext = alicepk.encapsulate()
    # Alice decapsulates the ciphertext from bob to derive the same shared secret
    alice_shared_secret = alicesk.decapsulate(ciphertext)
    # Print shared secrets in hex format
    print(f"Alice's Shared Secret : [{alice_shared_secret.sharedsecret.hex()}]")
    print(f"Bob's   Shared Secret : [{bob_shared_secret.sharedsecret.hex()}]")
    # Optional check
    assert alice_shared_secret.sharedsecret == bob_shared_secret.sharedsecret, "Shared secrets do not match!"

if __name__ == "__main__":
    main()
