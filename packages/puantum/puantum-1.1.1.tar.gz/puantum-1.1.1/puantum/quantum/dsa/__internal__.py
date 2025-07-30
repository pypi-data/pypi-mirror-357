# IMPORT
from puantum import __internal__ as _internal # type: ignore
import typing as _typing
import enum as _enum

# MAIN
class Algorithm:
    class CROSS(_enum.Enum):
        CROSSR128B = "CrossRsdp128Balanced"
        CROSSR128F = "CrossRsdp128Fast"
        CROSSR128S = "CrossRsdp128Small"
        CROSSR192B = "CrossRsdp192Balanced"
        CROSSR192F = "CrossRsdp192Fast"
        CROSSR192S = "CrossRsdp192Small"
        CROSSR256B = "CrossRsdp256Balanced"
        CROSSR256F = "CrossRsdp256Fast"
        CROSSR256S = "CrossRsdp256Small"
        CROSSRG128B = "CrossRsdpg128Balanced"
        CROSSRG128F = "CrossRsdpg128Fast"
        CROSSRG128S = "CrossRsdpg128Small"
        CROSSRG192B = "CrossRsdpg192Balanced"
        CROSSRG192F = "CrossRsdpg192Fast"
        CROSSRG192S = "CrossRsdpg192Small"
        CROSSRG256B = "CrossRsdpg256Balanced"
        CROSSRG256F = "CrossRsdpg256Fast"
        CROSSRG256S = "CrossRsdpg256Small"
    #
    class DILITHIUM(_enum.Enum):
        DILITHIUM2 = "Dilithium2"
        DILITHIUM3 = "Dilithium3"
        DILITHIUM5 = "Dilithium5"
    #
    class FALCON(_enum.Enum):
        FALCON512 = "Falcon512"
        FALCON1024 = "Falcon1024"
    #
    class MAYO(_enum.Enum):
        MAYO1 = "Mayo1"
        MAYO2 = "Mayo2"
        MAYO3 = "Mayo3"
        MAYO5 = "Mayo5"
    #
    class MLDSA(_enum.Enum):
        MLDSA44 = "MlDsa44"
        MLDSA65 = "MlDsa65"
        MLDSA87 = "MlDsa87"
    #
    class SPHINCS(_enum.Enum):
        SHA2128F = "SphincsSha2128fSimple"
        SHA2128S = "SphincsSha2128sSimple"
        SHA2192F = "SphincsSha2192fSimple"
        SHA2192S = "SphincsSha2192sSimple"
        SHA2256F = "SphincsSha2256fSimple"
        SHA2256S = "SphincsSha2256sSimple"
        SHAKE128F = "SphincsShake128fSimple"
        SHAKE128S = "SphincsShake128sSimple"
        SHAKE192F = "SphincsShake192fSimple"
        SHAKE192S = "SphincsShake192sSimple"
        SHAKE256F = "SphincsShake256fSimple"
        SHAKE256S = "SphincsShake256sSimple"
    #
    class UOV(_enum.Enum):
        UOVOVIII = "UovOvIII"
        UOVOVIIIPKC = "UovOvIIIPkc"
        UOVOVIIIPKCSKC = "UovOvIIIPkcSkc"
        UOVOVIP = "UovOvIp"
        UOVOVIPPKC = "UovOvIpPkc"
        UOVOVIPPKCSKC = "UovOvIpPkcSkc"
        UOVOVIS = "UovOvIs"
        UOVOVISPKC = "UovOvIsPkc"
        UOVOVISPKCSKC = "UovOvIsPkcSkc"
        UOVOVV = "UovOvV"
        UOVOVVPKC = "UovOvVPkc"
        UOVOVVPKCSKC = "UovOvVPkcSkc"



class Signature:
    def __init__(self, signature: bytes) -> None:
        if not isinstance(signature, bytes):
            raise TypeError("Signature Not Valid")
        #
        self.signature = signature
        #
        return None



class CROSSSignature(Signature):
    def __init__(self, name: Algorithm.CROSS, signature: bytes) -> None:
        if not isinstance(name, Algorithm.CROSS):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(signature)
        #
        return None



class DILITHIUMSignature(Signature):
    def __init__(self, name: Algorithm.DILITHIUM, signature: bytes) -> None:
        if not isinstance(name, Algorithm.DILITHIUM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(signature)
        #
        return None



class FALCONSignature(Signature):
    def __init__(self, name: Algorithm.FALCON, signature: bytes) -> None:
        if not isinstance(name, Algorithm.FALCON):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(signature)
        #
        return None



class MAYOSignature(Signature):
    def __init__(self, name: Algorithm.MAYO, signature: bytes) -> None:
        if not isinstance(name, Algorithm.MAYO):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(signature)
        #
        return None



class MLDSASignature(Signature):
    def __init__(self, name: Algorithm.MLDSA, signature: bytes) -> None:
        if not isinstance(name, Algorithm.MLDSA):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(signature)
        #
        return None



class SPHINCSSignature(Signature):
    def __init__(self, name: Algorithm.SPHINCS, signature: bytes) -> None:
        if not isinstance(name, Algorithm.SPHINCS):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(signature)
        #
        return None


class UOVSignature(Signature):
    def __init__(self, name: Algorithm.UOV, signature: bytes) -> None:
        if not isinstance(name, Algorithm.UOV):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(signature)
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
    def verify(self, signature: _typing.Any, message: _typing.Any) -> _typing.Any:
        raise NotImplementedError()



class CROSSPublicKey(PublicKey):
    def __init__(self, name: Algorithm.CROSS, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.CROSS):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def verify(self, signature: CROSSSignature, message: bytes) -> bool:
        result: bool = _internal.sigverify(self._algorithm.value, self.publickey, signature.signature, message) # type: ignore
        return result # type: ignore



class DILITHIUMPublicKey(PublicKey):
    def __init__(self, name: Algorithm.DILITHIUM, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.DILITHIUM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def verify(self, signature: DILITHIUMSignature, message: bytes) -> bool:
        result: bool = _internal.sigverify(self._algorithm.value, self.publickey, signature.signature, message) # type: ignore
        return result # type: ignore



class FALCONPublicKey(PublicKey):
    def __init__(self, name: Algorithm.FALCON, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.FALCON):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def verify(self, signature: FALCONSignature, message: bytes) -> bool:
        result: bool = _internal.sigverify(self._algorithm.value, self.publickey, signature.signature, message) # type: ignore
        return result # type: ignore



class MAYOPublicKey(PublicKey):
    def __init__(self, name: Algorithm.MAYO, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.MAYO):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def verify(self, signature: MAYOSignature, message: bytes) -> bool:
        result: bool = _internal.sigverify(self._algorithm.value, self.publickey, signature.signature, message) # type: ignore
        return result # type: ignore



class MLDSAPublicKey(PublicKey):
    def __init__(self, name: Algorithm.MLDSA, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.MLDSA):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def verify(self, signature: MLDSASignature, message: bytes) -> bool:
        result: bool = _internal.sigverify(self._algorithm.value, self.publickey, signature.signature, message) # type: ignore
        return result # type: ignore



class SPHINCSPublicKey(PublicKey):
    def __init__(self, name: Algorithm.SPHINCS, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.SPHINCS):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def verify(self, signature: SPHINCSSignature, message: bytes) -> bool:
        result: bool = _internal.sigverify(self._algorithm.value, self.publickey, signature.signature, message) # type: ignore
        return result # type: ignore



class UOVPublicKey(PublicKey):
    def __init__(self, name: Algorithm.UOV, publickey: bytes) -> None:
        if not isinstance(name, Algorithm.UOV):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(publickey)
        #
        self._algorithm = name
        #
        return None
    #
    def verify(self, signature: UOVSignature, message: bytes) -> bool:
        result: bool = _internal.sigverify(self._algorithm.value, self.publickey, signature.signature, message) # type: ignore
        return result # type: ignore



class SecretKey:
    def __init__(self, secretkey: bytes) -> None:
        if not isinstance(secretkey, bytes):
            raise TypeError("SecretKey Not Valid")
        #
        self.secretkey = secretkey
        #
        return None
    #
    def sign(self, message: _typing.Any) -> _typing.Any:
        raise NotImplementedError()



class CROSSSecretKey(SecretKey):
    def __init__(self, name: Algorithm.CROSS, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.CROSS):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def sign(self, message: bytes) -> CROSSSignature:
        signature: bytes = _internal.sigsign(self._algorithm.value, self.secretkey, message) # type: ignore
        return CROSSSignature(self._algorithm, signature) # type: ignore



class DILITHIUMSecretKey(SecretKey):
    def __init__(self, name: Algorithm.DILITHIUM, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.DILITHIUM):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def sign(self, message: bytes) -> DILITHIUMSignature:
        signature: bytes = _internal.sigsign(self._algorithm.value, self.secretkey, message) # type: ignore
        return DILITHIUMSignature(self._algorithm, signature) # type: ignore



class FALCONSecretKey(SecretKey):
    def __init__(self, name: Algorithm.FALCON, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.FALCON):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def sign(self, message: bytes) -> FALCONSignature:
        signature: bytes = _internal.sigsign(self._algorithm.value, self.secretkey, message) # type: ignore
        return FALCONSignature(self._algorithm, signature) # type: ignore



class MAYOSecretKey(SecretKey):
    def __init__(self, name: Algorithm.MAYO, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.MAYO):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def sign(self, message: bytes) -> MAYOSignature:
        signature: bytes = _internal.sigsign(self._algorithm.value, self.secretkey, message) # type: ignore
        return MAYOSignature(self._algorithm, signature) # type: ignore



class MLDSASecretKey(SecretKey):
    def __init__(self, name: Algorithm.MLDSA, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.MLDSA):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def sign(self, message: bytes) -> MLDSASignature:
        signature: bytes = _internal.sigsign(self._algorithm.value, self.secretkey, message) # type: ignore
        return MLDSASignature(self._algorithm, signature) # type: ignore



class SPHINCSSecretKey(SecretKey):
    def __init__(self, name: Algorithm.SPHINCS, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.SPHINCS):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def sign(self, message: bytes) -> SPHINCSSignature:
        signature: bytes = _internal.sigsign(self._algorithm.value, self.secretkey, message) # type: ignore
        return SPHINCSSignature(self._algorithm, signature) # type: ignore



class UOVSecretKey(SecretKey):
    def __init__(self, name: Algorithm.UOV, secretkey: bytes) -> None:
        if not isinstance(name, Algorithm.UOV):
            raise ValueError(f"Unsupported algorithm: {name}")
        else:
            super().__init__(secretkey)
        #
        self._algorithm = name
        #
        return None
    #
    def sign(self, message: bytes) -> UOVSignature:
        signature: bytes = _internal.sigsign(self._algorithm.value, self.secretkey, message) # type: ignore
        return UOVSignature(self._algorithm, signature) # type: ignore



Algorithms = Algorithm | Algorithm.CROSS | Algorithm.DILITHIUM | Algorithm.FALCON | Algorithm.MAYO | Algorithm.MLDSA | Algorithm.SPHINCS | Algorithm.UOV



@_typing.overload
def KeyPair(name: Algorithm) -> tuple[SecretKey, PublicKey]: ...


@_typing.overload
def KeyPair(name: Algorithm.CROSS) -> tuple[CROSSSecretKey, CROSSPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.DILITHIUM) -> tuple[DILITHIUMSecretKey, DILITHIUMPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.FALCON) -> tuple[FALCONSecretKey, FALCONPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.MAYO) -> tuple[MAYOSecretKey, MAYOPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.MLDSA) -> tuple[MLDSASecretKey, MLDSAPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.SPHINCS) -> tuple[SPHINCSSecretKey, SPHINCSPublicKey]: ...



@_typing.overload
def KeyPair(name: Algorithm.UOV) -> tuple[UOVSecretKey, UOVPublicKey]: ...



def KeyPair(name: Algorithms) -> tuple[SecretKey, PublicKey]:
    algorithm = name
    if isinstance(algorithm, Algorithm.CROSS):
        secretkey, publickey = _internal.sigkeygen(algorithm.value) # type: ignore
        return CROSSSecretKey(algorithm, secretkey), CROSSPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.DILITHIUM):
        secretkey, publickey = _internal.sigkeygen(algorithm.value) # type: ignore
        return DILITHIUMSecretKey(algorithm, secretkey), DILITHIUMPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.FALCON):
        secretkey, publickey = _internal.sigkeygen(algorithm.value) # type: ignore
        return FALCONSecretKey(algorithm, secretkey), FALCONPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.MAYO):
        secretkey, publickey = _internal.sigkeygen(algorithm.value) # type: ignore
        return MAYOSecretKey(algorithm, secretkey), MAYOPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.MLDSA):
        secretkey, publickey = _internal.sigkeygen(algorithm.value) # type: ignore
        return MLDSASecretKey(algorithm, secretkey), MLDSAPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.SPHINCS):
        secretkey, publickey = _internal.sigkeygen(algorithm.value) # type: ignore
        return SPHINCSSecretKey(algorithm, secretkey), SPHINCSPublicKey(algorithm, publickey) # type: ignore
    elif isinstance(algorithm, Algorithm.UOV):
        secretkey, publickey = _internal.sigkeygen(algorithm.value) # type: ignore
        return UOVSecretKey(algorithm, secretkey), UOVPublicKey(algorithm, publickey) # type: ignore
    else:
        raise ValueError(f"Unsupported algorithm: {name}")
