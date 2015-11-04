import mmh3 as mmh3

from icc.contentstorage.interfaces import IDocumentStorage

def hexdigest(digest):
    """Convert byte digest to
    hex digest
    Arguments:
    - `digest`: Byte array representing
    digest
    """
    if type(digest)==tuple:
        digest=joindigest(digest)
    if type(digest)==str:
        return digest		# implied, that string is a digest already
    if type(digest)==int:
        digest=bindigest(digest)
    return ''.join(["{:02x}".format(b) for b in digest])

def bindigest(digest):
    if type(digest)==tuple:
        digest=joindigest(digest)
    if type(digest)==str:
        return bytearray.fromhex(digest)
    if type(digest)==int:
        digest=digest.to_bytes(16, byteorder='little')
    return digest

def intdigest(digest):
    if type(digest)==tuple:
        digest=joindigest(digest)
    if type(digest)==int:
        return digest
    if type(digest)==str:
        digest=bytearray.fromhex(digest)
    return int.from_bytes(digest, byteorder='little')

def hash128(content):
    return mmh3.hash_bytes(content)

#def hash64(content):
#    return hash128(content)[4:12]

#def hash64_int(content):
#    return intdigest(hash64(content))

def hash128_int(content):
    return intdigest(hash128(content))

def splitdigest(digest):
    """Splits 128bit hash into two
    64bit numbers."""
    d=bindigest(digest)
    l,h=intdigest(d[:8]),intdigest(d[8:])
    return l,h

def joindigest(digest):
    l,h=digest
    l=bindigest(l)
    h=bindigest(h)
    return l+h

if __name__=="__main__":
    s='1'*100

    ih=hash128_int(s)
    bh=hash128(s)
    assert ih==intdigest(bh)
    assert hexdigest(ih)==hexdigest(bh)
    assert ih==intdigest(hexdigest(bindigest(ih)))
    assert ih==intdigest(splitdigest(ih))

    print ("Ok")
    quit()
