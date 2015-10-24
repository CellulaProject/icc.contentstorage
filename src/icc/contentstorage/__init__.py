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
