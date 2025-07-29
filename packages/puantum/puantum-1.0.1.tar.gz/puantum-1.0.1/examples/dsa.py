# IMPORT
from puantum.quantum.dsa import Algorithm, KeyPair

# MAIN
def main():
    # Step 1: Generate a digital signature key pair for Alice
    # - alicesk: Alice's private signing key
    # - alicepk: Alice's public key (used for verification)
    alicesk, alicepk = KeyPair(Algorithm.MLDSA.MLDSA87)
    # Step 2: Define the message to be signed
    msg = "Hello".encode()  # Convert the string to bytes, as cryptographic functions work with bytes
    # Step 3: Sign the message using Alice's private key
    sig = alicesk.sign(msg)
    # Step 4: Verify the signature using Alice's public key
    valid = alicepk.verify(sig, msg)
    # Step 5: Display the result
    print(f"Message          : {msg.decode()}")
    print(f"Signature valid? : {valid}")
    # Optional: raise an error if the signature fails (useful in tests)
    assert valid, "Signature verification failed!"

if __name__ == "__main__":
    main()
