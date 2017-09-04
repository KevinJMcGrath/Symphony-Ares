from Crypto.Hash import SHA256


def GetHash(inputStr):
    newHash = SHA256.new()
    newHash.update(inputStr.encode('utf-8'))
    return newHash


def CompareHashDigest(cleartext, compareToHash):
    newHash = SHA256.new(cleartext.encode('utf-8'))

    return newHash.hexdigest() == compareToHash
