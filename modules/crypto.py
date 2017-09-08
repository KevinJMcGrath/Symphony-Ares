# from Crypto.Hash import SHA256

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


def GetHash(inputStr):
    # newHash = SHA256.new()
    newHash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    newHash.update(inputStr.encode('utf-8'))

    hashBytes = newHash.finalize()


    return hashBytes.hex()


def CompareHashDigest(cleartext, compareToHash):
    # newHash = SHA256.new(cleartext.encode('utf-8'))

    return GetHash(cleartext) == compareToHash
