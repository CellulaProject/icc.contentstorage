import mmh3

def hexdigest(digest):
    """Convert byte digest to
    hex digest
    Arguments:
    - `digest`: Byte array representing
    digest
    """
    return ''.join(["{:02x}".format(b) for b in digest])

def bindigest(digest):
    return bytearray.fromhex(digest)

def hash_128(content):
    return mmh3.hash_bytes(content)

def hash_64(content):
    h=hash_128(content)[4:12]
