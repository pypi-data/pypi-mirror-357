class NTSLError(Exception): pass
class EncryptionError(NTSLError): pass
class DecryptionError(NTSLError): pass

class NTSLContextError(NTSLError): pass
class SignatureError(NTSLContextError): pass
class ExpirationError(NTSLContextError): pass
class MissingEntryError(NTSLContextError): pass
class KeyMismatchError(NTSLContextError): pass
class LoadOrderError(NTSLContextError): pass

class NTSLSocketError(NTSLError): pass
class MissingDataError(NTSLSocketError): pass
class HandshakeError(NTSLSocketError): pass
class ConnError(NTSLSocketError): pass