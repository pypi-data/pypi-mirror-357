# IMPORT
from puantum import __internal__ as _internal # type: ignore
import typing as _typing
import enum as _enum

# MAIN
class Algorithm:
    class BIKE(_enum.Enum):
        BIKEL1 = "BikeL1"
        BIKEL3 = "BikeL3"
        BIKEL5 = "BikeL5"
    #
    class CLASSICMCELIECE(_enum.Enum):
        CLASSICMCELIECE348864 = "ClassicMcEliece348864"
        CLASSICMCELIECE348864F = "ClassicMcEliece348864f"
        CLASSICMCELIECE460896 = "ClassicMcEliece460896"
        CLASSICMCELIECE460896F = "ClassicMcEliece460896f"
        CLASSICMCELIECE6688128 = "ClassicMcEliece6688128"
        CLASSICMCELIECE6688128F = "ClassicMcEliece6688128f"
        CLASSICMCELIECE6960119 = "ClassicMcEliece6960119"
        CLASSICMCELIECE6960119F = "ClassicMcEliece6960119f"
        CLASSICMCELIECE8192128 = "ClassicMcEliece8192128"
        CLASSICMCELIECE8192128F = "ClassicMcEliece8192128f"
    #
    class HQC(_enum.Enum):
        HQC128 = "Hqc128"
        HQC192 = "Hqc192"
        HQC256 = "Hqc256"
    #
    class KYBER(_enum.Enum):
        KYBER512 = "Kyber512"
        KYBER768 = "Kyber768"
        KYBER1024 = "Kyber1024"
    #
    class MLKEM(_enum.Enum):
        MLKEM512 = "MlKem512"
        MLKEM768 = "MlKem768"
        MLKEM1024 = "MlKem1024"
    #
    class NTRUPRIME(_enum.Enum):
        NTRUPRIME = "NtruPrimeSntrup761"
    #
    class FRODOKEM(_enum.Enum):
        FRODOKEM640AES = "FrodoKem640Aes"
        FRODOKEM640SHAKE = "FrodoKem640Shake"
        FRODOKEM976AES = "FrodoKem976Aes"
        FRODOKEM976SHAKE = "FrodoKem976Shake"
        FRODOKEM1344AES = "FrodoKem1344Aes"
        FRODOKEM1344SHAKE = "FrodoKem1344Shake"



class Ciphertext:
    def __init__(self, ciphertext: bytes) -> None:
        if not isinstance(ciphertext, bytes):
            raise TypeError("Ciphertext Not Valid")
        #
        self.ciphertext = ciphertext
        #
        return None



class BIKECiphertext(Ciphertext):
    def __init__(self, name: Algorithm.BIKE, ciphertext: bytes) -> None:
        if not isinstance(name, Algorithm.BIKE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(ciphertext)
        #
        return None



class CLASSICMCELIECECiphertext(Ciphertext):
    def __init__(self, name: Algorithm.CLASSICMCELIECE, ciphertext: bytes) -> None:
        if not isinstance(name, Algorithm.CLASSICMCELIECE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(ciphertext)
        #
        return None



class HQCCiphertext(Ciphertext):
    def __init__(self, name: Algorithm.HQC, ciphertext: bytes) -> None:
        if not isinstance(name, Algorithm.HQC):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(ciphertext)
        #
        return None



class KYBERCiphertext(Ciphertext):
    def __init__(self, name: Algorithm.KYBER, ciphertext: bytes) -> None:
        if not isinstance(name, Algorithm.KYBER):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(ciphertext)
        #
        return None



class MLKEMCiphertext(Ciphertext):
    def __init__(self, name: Algorithm.MLKEM, ciphertext: bytes) -> None:
        if not isinstance(name, Algorithm.MLKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(ciphertext)
        #
        return None



class NTRUPRIMECiphertext(Ciphertext):
    def __init__(self, name: Algorithm.NTRUPRIME, ciphertext: bytes) -> None:
        if not isinstance(name, Algorithm.NTRUPRIME):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(ciphertext)
        #
        return None



class FRODOKEMCiphertext(Ciphertext):
    def __init__(self, name: Algorithm.FRODOKEM, ciphertext: bytes) -> None:
        if not isinstance(name, Algorithm.FRODOKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(ciphertext)
        #
        return None



class SharedSecret:
    def __init__(self, sharedsecret: bytes) -> None:
        if not isinstance(sharedsecret, bytes):
            raise TypeError("SharedSecret Not Valid")
        #
        self.sharedsecret = sharedsecret
        #
        return None



class BIKESharedSecret(SharedSecret):
    def __init__(self, name: Algorithm.BIKE, sharedsecret: bytes) -> None:
        if not isinstance(name, Algorithm.BIKE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(sharedsecret)
        #
        return None



class CLASSICMCELIECESharedSecret(SharedSecret):
    def __init__(self, name: Algorithm.CLASSICMCELIECE, sharedsecret: bytes) -> None:
        if not isinstance(name, Algorithm.CLASSICMCELIECE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(sharedsecret)
        #
        return None



class HQCSharedSecret(SharedSecret):
    def __init__(self, name: Algorithm.HQC, sharedsecret: bytes) -> None:
        if not isinstance(name, Algorithm.HQC):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(sharedsecret)
        #
        return None



class KYBERSharedSecret(SharedSecret):
    def __init__(self, name: Algorithm.KYBER, sharedsecret: bytes) -> None:
        if not isinstance(name, Algorithm.KYBER):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(sharedsecret)
        #
        return None



class MLKEMSharedSecret(SharedSecret):
    def __init__(self, name: Algorithm.MLKEM, sharedsecret: bytes) -> None:
        if not isinstance(name, Algorithm.MLKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(sharedsecret)
        #
        return None



class NTRUPRIMESharedSecret(SharedSecret):
    def __init__(self, name: Algorithm.NTRUPRIME, sharedsecret: bytes) -> None:
        if not isinstance(name, Algorithm.NTRUPRIME):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(sharedsecret)
        #
        return None



class FRODOKEMSharedSecret(SharedSecret):
    def __init__(self, name: Algorithm.FRODOKEM, sharedsecret: bytes) -> None:
        if not isinstance(name, Algorithm.FRODOKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(sharedsecret)
        #
        return None



class PublicKey:
    def __init__(self, publickey: bytes) -> None:
        if not isinstance(publickey, bytes):
            raise TypeError("PublicKey Not Valid")
        #
        self.publickey = publickey
        #
        return None
    #
    def encapsulate(self) -> tuple[_typing.Any, _typing.Any]:
        raise NotImplementedError()



class BIKEPublicKey(PublicKey):
    def __init__(self, name: Algorithm.BIKE, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.BIKE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def encapsulate(self) -> tuple[BIKESharedSecret, BIKECiphertext]:
        sharedsecret, ciphertext = _internal.kemencapsulate(self._algorithm.value, self.publickey) # type: ignore
        return BIKESharedSecret(self._algorithm, sharedsecret), BIKECiphertext(self._algorithm, ciphertext) # type: ignore



class CLASSICMCELIECEPublicKey(PublicKey):
    def __init__(self, name: Algorithm.CLASSICMCELIECE, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.CLASSICMCELIECE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def encapsulate(self) -> tuple[CLASSICMCELIECESharedSecret, CLASSICMCELIECECiphertext]:
        sharedsecret, ciphertext = _internal.kemencapsulate(self._algorithm.value, self.publickey) # type: ignore
        return CLASSICMCELIECESharedSecret(self._algorithm, sharedsecret), CLASSICMCELIECECiphertext(self._algorithm, ciphertext) # type: ignore



class HQCPublicKey(PublicKey):
    def __init__(self, name: Algorithm.HQC, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.HQC):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def encapsulate(self) -> tuple[HQCSharedSecret, HQCCiphertext]:
        sharedsecret, ciphertext = _internal.kemencapsulate(self._algorithm.value, self.publickey) # type: ignore
        return HQCSharedSecret(self._algorithm, sharedsecret), HQCCiphertext(self._algorithm, ciphertext) # type: ignore



class KYBERPublicKey(PublicKey):
    def __init__(self, name: Algorithm.KYBER, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.KYBER):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def encapsulate(self) -> tuple[KYBERSharedSecret, KYBERCiphertext]:
        sharedsecret, ciphertext = _internal.kemencapsulate(self._algorithm.value, self.publickey) # type: ignore
        return KYBERSharedSecret(self._algorithm, sharedsecret), KYBERCiphertext(self._algorithm, ciphertext) # type: ignore



class MLKEMPublicKey(PublicKey):
    def __init__(self, name: Algorithm.MLKEM, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.MLKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def encapsulate(self) -> tuple[MLKEMSharedSecret, MLKEMCiphertext]:
        sharedsecret, ciphertext = _internal.kemencapsulate(self._algorithm.value, self.publickey) # type: ignore
        return MLKEMSharedSecret(self._algorithm, sharedsecret), MLKEMCiphertext(self._algorithm, ciphertext) # type: ignore



class NTRUPRIMEPublicKey(PublicKey):
    def __init__(self, name: Algorithm.NTRUPRIME, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.NTRUPRIME):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def encapsulate(self) -> tuple[NTRUPRIMESharedSecret, NTRUPRIMECiphertext]:
        sharedsecret, ciphertext = _internal.kemencapsulate(self._algorithm.value, self.publickey) # type: ignore
        return NTRUPRIMESharedSecret(self._algorithm, sharedsecret), NTRUPRIMECiphertext(self._algorithm, ciphertext) # type: ignore



class FRODOKEMPublicKey(PublicKey):
    def __init__(self, name: Algorithm.FRODOKEM, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.FRODOKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def encapsulate(self) -> tuple[FRODOKEMSharedSecret, FRODOKEMCiphertext]:
        sharedsecret, ciphertext = _internal.kemencapsulate(self._algorithm.value, self.publickey) # type: ignore
        return FRODOKEMSharedSecret(self._algorithm, sharedsecret), FRODOKEMCiphertext(self._algorithm, ciphertext) # type: ignore



class SecretKey:
    def __init__(self, secretkey: bytes) -> None:
        if not isinstance(secretkey, bytes):
            raise TypeError("SecretKey Not Valid")
        #
        self.secretkey = secretkey
        #
        return None
    #
    def decapsulate(self, ciphertext: _typing.Any) -> _typing.Any:
        raise NotImplementedError()



class BIKESecretKey(SecretKey):
    def __init__(self, name: Algorithm.BIKE, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.BIKE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def decapsulate(self, ciphertext: BIKECiphertext) -> BIKESharedSecret:
        sharedsecret: bytes = _internal.kemdecapsulate(self._algorithm.value, self.secretkey, ciphertext.ciphertext) # type: ignore
        return BIKESharedSecret(self._algorithm, sharedsecret) # type: ignore



class CLASSICMCELIECESecretKey(SecretKey):
    def __init__(self, name: Algorithm.CLASSICMCELIECE, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.CLASSICMCELIECE):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def decapsulate(self, ciphertext: CLASSICMCELIECECiphertext) -> CLASSICMCELIECESharedSecret:
        sharedsecret: bytes = _internal.kemdecapsulate(self._algorithm.value, self.secretkey, ciphertext.ciphertext) # type: ignore
        return CLASSICMCELIECESharedSecret(self._algorithm, sharedsecret) # type: ignore



class HQCSecretKey(SecretKey):
    def __init__(self, name: Algorithm.HQC, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.HQC):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def decapsulate(self, ciphertext: HQCCiphertext) -> HQCSharedSecret:
        sharedsecret: bytes = _internal.kemdecapsulate(self._algorithm.value, self.secretkey, ciphertext.ciphertext) # type: ignore
        return HQCSharedSecret(self._algorithm, sharedsecret) # type: ignore



class KYBERSecretKey(SecretKey):
    def __init__(self, name: Algorithm.KYBER, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.KYBER):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def decapsulate(self, ciphertext: KYBERCiphertext) -> KYBERSharedSecret:
        sharedsecret: bytes = _internal.kemdecapsulate(self._algorithm.value, self.secretkey, ciphertext.ciphertext) # type: ignore
        return KYBERSharedSecret(self._algorithm, sharedsecret) # type: ignore



class MLKEMSecretKey(SecretKey):
    def __init__(self, name: Algorithm.MLKEM, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.MLKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def decapsulate(self, ciphertext: MLKEMCiphertext) -> MLKEMSharedSecret:
        sharedsecret: bytes = _internal.kemdecapsulate(self._algorithm.value, self.secretkey, ciphertext.ciphertext) # type: ignore
        return MLKEMSharedSecret(self._algorithm, sharedsecret) # type: ignore



class NTRUPRIMESecretKey(SecretKey):
    def __init__(self, name: Algorithm.NTRUPRIME, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.NTRUPRIME):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def decapsulate(self, ciphertext: NTRUPRIMECiphertext) -> NTRUPRIMESharedSecret:
        sharedsecret: bytes = _internal.kemdecapsulate(self._algorithm.value, self.secretkey, ciphertext.ciphertext) # type: ignore
        return NTRUPRIMESharedSecret(self._algorithm, sharedsecret) # type: ignore



class FRODOKEMSecretKey(SecretKey):
    def __init__(self, name: Algorithm.FRODOKEM, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.FRODOKEM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def decapsulate(self, ciphertext: FRODOKEMCiphertext) -> FRODOKEMSharedSecret:
        sharedsecret: bytes = _internal.kemdecapsulate(self._algorithm.value, self.secretkey, ciphertext.ciphertext) # type: ignore
        return FRODOKEMSharedSecret(self._algorithm, sharedsecret) # type: ignore



Algorithms = Algorithm | Algorithm.BIKE | Algorithm.CLASSICMCELIECE | Algorithm.HQC | Algorithm.KYBER | Algorithm.MLKEM | Algorithm.NTRUPRIME | Algorithm.FRODOKEM



@_typing.overload
def KeyPair(name: Algorithm) -> tuple[SecretKey, PublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.BIKE) -> tuple[BIKESecretKey, BIKEPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.CLASSICMCELIECE) -> tuple[CLASSICMCELIECESecretKey, CLASSICMCELIECEPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.HQC) -> tuple[HQCSecretKey, HQCPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.KYBER) -> tuple[KYBERSecretKey, KYBERPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.MLKEM) -> tuple[MLKEMSecretKey, MLKEMPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.NTRUPRIME) -> tuple[NTRUPRIMESecretKey, NTRUPRIMEPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.FRODOKEM) -> tuple[FRODOKEMSecretKey, FRODOKEMPublicKey]: ...



def KeyPair(name: Algorithms) -> tuple[SecretKey, PublicKey]:
    algorithm = name
    if isinstance(algorithm, Algorithm.BIKE):
        secretkey, publickey = _internal.kemkeygen(algorithm.value) # type: ignore
        return BIKESecretKey(algorithm, secretkey), BIKEPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.CLASSICMCELIECE):
        secretkey, publickey = _internal.kemkeygen(algorithm.value) # type: ignore
        return CLASSICMCELIECESecretKey(algorithm, secretkey), CLASSICMCELIECEPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.HQC):
        secretkey, publickey = _internal.kemkeygen(algorithm.value) # type: ignore
        return HQCSecretKey(algorithm, secretkey), HQCPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.KYBER):
        secretkey, publickey = _internal.kemkeygen(algorithm.value) # type: ignore
        return KYBERSecretKey(algorithm, secretkey), KYBERPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.MLKEM):
        secretkey, publickey = _internal.kemkeygen(algorithm.value) # type: ignore
        return MLKEMSecretKey(algorithm, secretkey), MLKEMPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.NTRUPRIME):
        secretkey, publickey = _internal.kemkeygen(algorithm.value) # type: ignore
        return NTRUPRIMESecretKey(algorithm, secretkey), NTRUPRIMEPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.FRODOKEM):
        secretkey, publickey = _internal.kemkeygen(algorithm.value) # type: ignore
        return FRODOKEMSecretKey(algorithm, secretkey), FRODOKEMPublicKey(algorithm, publickey) # type: ignore
    else:
        raise ValueError(f"Unsupported algorithm: {name}")
