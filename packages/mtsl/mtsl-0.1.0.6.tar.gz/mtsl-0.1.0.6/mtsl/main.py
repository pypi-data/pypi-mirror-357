import os
import secrets
import socket

from datetime import datetime, timezone

from pyelle import ELLEFile, elle_decode, ELLEEntry

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from argon2.low_level import hash_secret_raw, Type

from .exceptions import *


class MTSLContext:

    def __init__(self):
        self._authority_public_key: ed25519.Ed25519PublicKey | None = None
        self._public_key: ed25519.Ed25519PublicKey | None = None
        self._private_key: ed25519.Ed25519PrivateKey | None  = None
        self._public_file: ELLEFile | None = None

    def authority_file(self, authority_file: str) -> None:
        if not os.path.exists(authority_file):
            raise FileNotFoundError(authority_file)

        authority = ELLEFile(authority_file)

        authority_public_key_entry = authority.find_entry_with_name('PUBLIC KEY')

        if not authority_public_key_entry:
            raise MissingEntryError(f"{authority_file} does not have required entry 'PUBLIC KEY'")

        authority_public_key_bytes = authority_public_key_entry.value
        self._authority_public_key = ed25519.Ed25519PublicKey.from_public_bytes(authority_public_key_bytes)

    def validate_pub_str(self, pub_file: str) -> tuple[ed25519.Ed25519PublicKey, bytes, ELLEFile]:
        pub = elle_decode(pub_file)

        pk_entry = pub.find_entry_with_name('PUBLIC KEY')
        pk_sig_entry = pub.find_entry_with_name('PUBLIC KEY SIGNATURE')
        expr_entry = pub.find_entry_with_name('EXPR_DATE')
        auth_sig_entry = pub.find_entry_with_name('AUTHORITY SIGNATURE')

        missing = [
            name for name, entry in [
                ('PUBLIC KEY', pk_entry),
                ('PUBLIC KEY SIGNATURE', pk_sig_entry),
                ('EXPR_DATE', expr_entry),
                ('AUTHORITY SIGNATURE', auth_sig_entry)
            ] if not entry
        ]
        if missing:
            raise MissingEntryError(f"{pub_file} is missing required entries: {', '.join(missing)}")

        pk_bytes = pk_entry.value
        pk_sig = pk_sig_entry.value
        expr_str = expr_entry.value.decode()
        auth_sig = auth_sig_entry.value

        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pk_bytes)

        try:
            public_key.verify(pk_sig, pk_bytes)
        except InvalidSignature:
            raise SignatureError(f"{pub_file} contains invalid signature for public key.")

        signed_data = str(ELLEFile(
            data_name='PUBLIC KEY',
            values=(pk_entry, pk_sig_entry, expr_entry)
        )).encode()

        try:
            self._authority_public_key.verify(auth_sig, signed_data)
        except InvalidSignature:
            raise SignatureError(f"{pub_file} contains invalid authority signature.")

        expr_time = datetime.strptime(expr_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expr_time:
            raise ExpirationError(f"{pub_file} is expired.")

        return public_key, pk_bytes, pub

    def _validate_load_sec(self, sec_file: str, pk_bytes: bytes) -> ed25519.Ed25519PrivateKey:
        sec = ELLEFile(sec_file)
        sk_entry = sec.find_entry_with_name('PRIVATE KEY')

        if not sk_entry:
            raise MissingEntryError(f"{sec_file} does not have required entry 'PRIVATE KEY'")

        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(sk_entry.value)

        recreated_pk_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        if recreated_pk_bytes != pk_bytes:
            raise KeyMismatchError(f"Subject files contain mismatched public/private keys.")

        return private_key

    def subject_files(self, pub_file: str, sec_file: str) -> None:
        if not self._authority_public_key:
            raise LoadOrderError("Authority file must be loaded before subject files.")

        if not os.path.exists(pub_file):
            raise FileNotFoundError(pub_file)

        if not os.path.exists(sec_file):
            raise FileNotFoundError(sec_file)

        public_key, pk_bytes, pub = self.validate_pub_str(str(ELLEFile(pub_file)))
        private_key = self._validate_load_sec(sec_file, pk_bytes)

        self._public_key = public_key
        self._private_key = private_key
        self._public_file = pub

    def get_pub_data(self) -> bytes:
        return str(self._public_file).encode()

    def sign_data(self, data: bytes) -> bytes:
        return self._private_key.sign(data)

    def wrap_socket(self, sock: socket.socket) -> 'MTSLSocket':
        return MTSLSocket(sock, self)



class MTSLSocket:

    def _handshake(self):
        pub_data = self.ctx.get_pub_data()
        self._insecure_sendall(pub_data)

        other_pub_data = self._insecure_await_recv()
        self._other_public_key, _, _ = self.ctx.validate_pub_str(other_pub_data.decode())

        random_data = secrets.token_bytes(128)
        signing_challenge = str(ELLEFile(
            data_name='SIGNING CHALLENGE',
            values=(ELLEEntry("DATA", (), random_data),)
        )).encode()
        self._insecure_sendall(signing_challenge)

        other_signing_challenge = self._insecure_await_recv()
        other_signing_challenge_file = elle_decode(other_signing_challenge.decode())
        to_sign = other_signing_challenge_file.find_entry_with_name('DATA')
        signature = self.ctx.sign_data(to_sign.value)
        signed_challenge = str(ELLEFile(
            data_name='CHALLENGE SIGNATURE',
            values=(ELLEEntry("SIGNATURE", (), signature),)
        )).encode()
        self._insecure_sendall(signed_challenge)

        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        other_challenge_signature = self._insecure_await_recv()
        other_challenge_signature_file = elle_decode(other_challenge_signature.decode())
        other_signature = other_challenge_signature_file.find_entry_with_name('SIGNATURE').value
        self._other_public_key.verify(other_signature, random_data)

        signature = self.ctx.sign_data(public_bytes)
        public_key_info = str(ELLEFile(
            data_name='PUBLIC KEY INFO',
            values=(
                ELLEEntry("PUBLIC KEY", (), public_bytes),
                ELLEEntry("PUBLIC KEY SIGNATURE", (), signature),
            ))).encode()
        self._insecure_sendall(public_key_info)

        other_public_key_info = self._insecure_await_recv()
        other_public_key_info_file = elle_decode(other_public_key_info.decode())
        other_public_bytes = other_public_key_info_file.find_entry_with_name('PUBLIC KEY')
        other_public_key_sig = other_public_key_info_file.find_entry_with_name('PUBLIC KEY SIGNATURE')
        other_public_key = x25519.X25519PublicKey.from_public_bytes(other_public_bytes.value)
        other_pub_file = elle_decode(other_pub_data.decode())
        other_verification_bytes = other_pub_file.find_entry_with_name('PUBLIC KEY').value
        other_verification_key = ed25519.Ed25519PublicKey.from_public_bytes(other_verification_bytes)
        other_verification_key.verify(other_public_key_sig.value, other_public_bytes.value)

        decrypt_salt = secrets.token_bytes(16)
        salt_info = str(ELLEFile(
            data_name='SALT INFO',
            values=(
                ELLEEntry("KEY SALT", (), decrypt_salt),
            ))).encode()
        self._insecure_sendall(salt_info)

        shared_secret = private_key.exchange(other_public_key)
        salt_file_str = self._insecure_await_recv()
        salt_file = elle_decode(salt_file_str.decode())
        encrypt_salt = salt_file.find_entry_with_name('KEY SALT').value

        self._encrypt_key = self._derive_master_key(shared_secret, salt=encrypt_salt)
        self._decrypt_key = self._derive_master_key(shared_secret, salt=decrypt_salt)

    def __init__(self, sock: socket.socket, context: MTSLContext) -> None:
        self._sock = sock
        self.ctx = context

        self._handshake()


    def _insecure_await_recv(self, data_len=None) -> bytes:
        """
        DO NOT USE
        FOR HANDSHAKE ONLY

        :return: bytes
        """
        while True:
            if data_len is None:
                data_len = int.from_bytes(self._sock.recv(4), byteorder='little')
            data = self._sock.recv(data_len)

            if data:
               break

        return data

    def _insecure_sendall(self, data: bytes) -> None:
        data_len = len(data)
        data_len_bytes = data_len.to_bytes(4, byteorder='little')
        self._sock.sendall(data_len_bytes)
        self._sock.sendall(data)

    def _derive_master_key(self, shared_secret: bytes, salt) -> bytes:
        return hash_secret_raw(
            secret=shared_secret,
            salt=salt,
            time_cost=6,
            memory_cost=2 ** 20,
            parallelism=2,
            hash_len=32,
            type=Type.ID
        )

    def _derive_message_key(self, master_key: bytes, salt: bytes) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"MESSAGE_KEY"
        ).derive(master_key)

    def send(self, data: bytes) -> None:
        message_nonce = secrets.token_bytes(12)
        message_salt = secrets.token_bytes(16)
        message_key = self._derive_message_key(self._encrypt_key, message_salt)
        ciphertext = AESGCM(message_key).encrypt(message_nonce, data, None)

        elle_message = str(ELLEFile(
            data_name='PACKET',
            values=(
                ELLEEntry("NONCE", (), message_nonce),
                ELLEEntry("SALT", (), message_salt),
                ELLEEntry("CIPHERTEXT", (), ciphertext),
            )
        )).encode()

        msg_len = len(elle_message)
        msg_len_bytes = msg_len.to_bytes(4, byteorder='little')

        self._sock.sendall(msg_len_bytes)
        self._sock.sendall(elle_message)

    def recv(self) -> bytes:
        msg_len_bytes = b''
        while True:
            chunk = self._sock.recv(4 - len(msg_len_bytes))
            msg_len_bytes += chunk
            if len(msg_len_bytes) == 4:
                break

        msg_len = int.from_bytes(msg_len_bytes, byteorder='little')

        data = b''
        while True:
            chunk = self._sock.recv(msg_len - len(data))
            data += chunk
            if len(data) == msg_len:
                break

        elle_data = elle_decode(data.decode())

        c = elle_data.find_entry_with_name('CIPHERTEXT').value
        salt = elle_data.find_entry_with_name('SALT').value
        nonce = elle_data.find_entry_with_name('NONCE').value

        message_key = self._derive_message_key(self._decrypt_key, salt)

        p = AESGCM(message_key).decrypt(nonce, c, None)

        return p

    def close(self):
        self._sock.close()
