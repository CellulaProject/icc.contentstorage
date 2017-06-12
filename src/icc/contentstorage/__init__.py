import mmh3 as mmh3

from icc.contentstorage.interfaces import IContentStorage


def hexdigest(digest):
    """Convert byte digest to
    hex digest
    Arguments:
    - `digest`: Byte array representing
    digest
    """
    if type(digest) in (tuple, list):
        digest = joindigest(digest)
    if type(digest) == str:
        return digest		# implied, that string is a digest already
    if type(digest) == int:
        digest = bindigest(digest)
    return ''.join(["{:02x}".format(b) for b in digest])


def bindigest(digest, bs=16):
    if type(digest) in (tuple, list):
        digest = joindigest(digest)
    if type(digest) == str:
        return bytearray.fromhex(digest)
    if type(digest) == int:
        digest = digest.to_bytes(bs, byteorder='little')
    return digest


def intdigest(digest):
    if type(digest) in (tuple, list):
        digest = joindigest(digest)
    if type(digest) == int:
        return digest
    if type(digest) == str:
        digest = bytearray.fromhex(digest)
    return int.from_bytes(digest, byteorder='little')


def hash128(content):
    return mmh3.hash_bytes(content)

# def hash64(content):
#    return hash128(content)[4:12]

# def hash64_int(content):
#    return intdigest(hash64(content))


def hash128_int(content):
    return intdigest(hash128(content))


def splitdigest(digest):
    """Splits 128bit hash into two
    64bit numbers."""
    d = bindigest(digest)
    l, h = intdigest(d[:8]), intdigest(d[8:])
    return l, h


two64 = 1 << 64


def joindigest(digest):
    l, h = digest
    if l < 0:
        l = two64 - l
    if h < 0:
        h = two64 - h
    l = bindigest(l, bs=8)
    h = bindigest(h, bs=8)
    return l + h


COMP_MIMES = set([
    # https://en.wikipedia.org/wiki/List_of_archive_formats

    "application/x-bzip",
    "application/x-cpio",
    "application/x-shar",
    "application/x-tar",
    "application/x-bzip2",
    "application/x-gzip",
    "application/x-lzip",
    "application/x-lzma",
    "application/x-lzop",
    "application/x-snappy-framed",
    "application/x-xz",
    "application/x-compress",
    "application/x-7z-compressed",
    "application/x-ace-compressed",
    "application/x-astrotite-afa",
    "application/x-alz-compressed",
    "application/vnd.android.package-archive",
    "application/x-arj",
    "application/x-b1",
    "application/vnd.ms-cab-compressed",
    "application/x-dar",
    "application/x-dgc-compressed",
    "application/x-apple-diskimage",
    "application/x-gca-compressed",
    "application/x-lzh",
    "application/x-lzx",
    "application/x-rar-compressed",
    "application/x-stuffit",
    "application/x-stuffitx",
    "application/x-gtar",
    "application/zip",
    "application/x-zoo",
    "application/x-par2",
    "image/vnd.djvu",
])

COMP_EXT = set([
    ".gz",
    ".bz2",
    ".xz",
    ".zip",
    ".rar",
    ".lha",
    ".jpg",
    ".png",
    ".tiff",
    ".docx",
    ".pptx",
    ".odt",
    ".odp",
    ".7z",
    ".djvu",
    # FIXME Add more
])


if __name__ == "__main__":
    s = '1' * 100

    ih = hash128_int(s)
    bh = hash128(s)
    assert ih == intdigest(bh)
    assert hexdigest(ih) == hexdigest(bh)
    assert ih == intdigest(hexdigest(bindigest(ih)))
    assert ih == intdigest(splitdigest(ih))

    print("Ok")
    quit()
