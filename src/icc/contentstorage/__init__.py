import mmh3 as mmh3

def hexdigest(digest):
    """Convert byte digest to
    hex digest
    Arguments:
    - `digest`: Byte array representing
    digest
    """
    if type(digest)==str:
        return digest		# implied, that string is a digest already
    if type(digest)==int:
        digest=bindigest(digest)
    return ''.join(["{:02x}".format(b) for b in digest])

def bindigest(digest):
    if type(digest)==str:
        return bytearray.fromhex(digest)
    if type(digest)==int:
        digest=digest.to_bytes(8, byteorder='little')
    return digest

def intdigest(digest):
    if type(digest)==int:
        return digest
    if type(digest)==str:
        digest=bytearray.fromhex(digest)
    return int.from_bytes(digest, byteorder='little')

def hash128(content):
    return mmh3.hash_bytes(content)

def hash64(content):
    return hash128(content)[4:12]

def hash64_int(content):
    return intdigest(hash64(content))

if __name__=="__main__":
    s='1'*100

    ih=hash64_int(s)
    bh=hash64(s)
    assert ih==intdigest(bh)
    assert hexdigest(ih)==hexdigest(bh)
    assert ih==intdigest(hexdigest(bindigest(ih)))

    print ("Ok")
    quit()
