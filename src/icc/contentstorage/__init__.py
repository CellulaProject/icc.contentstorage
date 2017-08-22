import mmh3 as mmh3


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


GOOD_MIMES = set([
    "application/marc",
    "application/marcxml+xml",
    "application/mbox",
    "application/msword",
    "application/pdf",
    "application/pls+xml",
    "application/postscript",
    "application/rdf+xml",
    "application/rss+xml",
    "application/rtf",
    "application/sparql-query",
    "application/sparql-results+xml",
    "application/vnd.amazon.ebook",
    "application/vnd.google-earth.kml+xml",
    "application/vnd.google-earth.kmz",
    "application/vnd.mozilla.xul+xml",
    "application/vnd.ms-excel",
    "application/vnd.ms-excel.addin.macroenabled.12",
    "application/vnd.ms-excel.sheet.binary.macroenabled.12",
    "application/vnd.ms-excel.sheet.macroenabled.12",
    "application/vnd.ms-excel.template.macroenabled.12",
    "application/vnd.ms-htmlhelp",
    "application/vnd.ms-officetheme",
    "application/vnd.ms-pki.seccat",
    "application/vnd.ms-pki.stl",
    "application/vnd.ms-powerpoint",
    "application/vnd.ms-powerpoint.addin.macroenabled.12",
    "application/vnd.ms-powerpoint.presentation.macroenabled.12",
    "application/vnd.ms-powerpoint.slide.macroenabled.12",
    "application/vnd.ms-powerpoint.slideshow.macroenabled.12",
    "application/vnd.ms-powerpoint.template.macroenabled.12",
    "application/vnd.ms-project",
    "application/vnd.ms-word.document.macroenabled.12",
    "application/vnd.ms-word.template.macroenabled.12",
    "application/vnd.ms-works",
    "application/vnd.ms-wpl",
    "application/vnd.ms-xpsdocument",
    "application/vnd.oasis.opendocument.chart",
    "application/vnd.oasis.opendocument.chart-template",
    "application/vnd.oasis.opendocument.database",
    "application/vnd.oasis.opendocument.formula",
    "application/vnd.oasis.opendocument.formula-template",
    "application/vnd.oasis.opendocument.graphics",
    "application/vnd.oasis.opendocument.graphics-template",
    "application/vnd.oasis.opendocument.image",
    "application/vnd.oasis.opendocument.image-template",
    "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.presentation-template",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.spreadsheet-template",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.text-master",
    "application/vnd.oasis.opendocument.text-template",
    "application/vnd.oasis.opendocument.text-web",
    "application/vnd.openofficeorg.extension",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.presentationml.slide",
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
    "application/vnd.openxmlformats-officedocument.presentationml.template",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    "application/vnd.recordare.musicxml",
    "application/vnd.recordare.musicxml+xml",
    "application/vnd.stardivision.calc",
    "application/vnd.stardivision.draw",
    "application/vnd.stardivision.impress",
    "application/vnd.stardivision.math",
    "application/vnd.stardivision.writer",
    "application/vnd.stardivision.writer-global",
    "application/vnd.sun.xml.calc",
    "application/vnd.sun.xml.calc.template",
    "application/vnd.sun.xml.draw",
    "application/vnd.sun.xml.draw.template",
    "application/vnd.sun.xml.impress",
    "application/vnd.sun.xml.impress.template",
    "application/vnd.sun.xml.math",
    "application/vnd.sun.xml.writer",
    "application/vnd.sun.xml.writer.global",
    "application/vnd.sun.xml.writer.template",
    "application/vnd.sus-calendar",
    "application/vnd.visio",
    "application/vnd.visio2013",
    "application/vnd.wap.wbxml",
    "application/vnd.wap.wmlc",
    "application/vnd.wap.wmlscriptc",
    "application/vnd.wolfram.player",
    "application/vnd.wordperfect",
    "application/vnd.wqd",
    "application/vnd.zul",
    "application/widget",
    "application/x-abiword",
    "application/x-dvi",
    "application/x-gnumeric",
    "application/x-java-jnlp-file",
    "application/x-latex",
    "application/x-mobipocket-ebook",
    "application/x-ms-application",
    "application/x-ms-wmd",
    "application/x-ms-wmz",
    "application/x-msaccess",
    "application/x-msbinder",
    "application/x-mscardfile",
    "application/x-msclip",
    "application/x-msdownload",
    "application/x-msmediaview",
    "application/x-msmetafile",
    "application/x-msmoney",
    "application/x-mspublisher",
    "application/x-msschedule",
    "application/x-msterminal",
    "application/x-mswrite",
    "application/x-netcdf",
    "application/x-tcl",
    "application/x-tex",
    "application/x-tex-tfm",
    "application/x-texinfo",
    "application/x-xfig",
    "application/x-xpinstall",
    "application/xcap-diff+xml",
    "application/xenc+xml",
    "application/xhtml+xml",
    "application/xml",
    "application/xml-dtd",
    "application/xop+xml",
    "application/xslt+xml",
    "application/xspf+xml",
    "application/xv+xml",
    "message/rfc822",
    "model/iges",
    "model/mesh",
    "model/vnd.collada+xml",
    "model/vnd.dwf",
    "model/vnd.gdl",
    "model/vnd.gtw",
    "model/vnd.mts",
    "model/vnd.vtu",
    "model/vrml",
    "text/calendar",
    "text/css",
    "text/csv",
    "text/html",
    "text/n3",
    "text/plain",
    "text/plain-bas",
    "text/prs.lines.tag",
    "text/richtext",
    "text/sgml",
    "text/tab-separated-values",
    "text/troff",
    "text/turtle",
    "text/uri-list",
    "text/vnd.curl",
    "text/vnd.curl.dcurl",
    "text/vnd.curl.mcurl",
    "text/vnd.curl.scurl",
    "text/vnd.fly",
    "text/vnd.fmi.flexstor",
    "text/vnd.graphviz",
    "text/vnd.in3d.3dml",
    "text/vnd.in3d.spot",
    "text/vnd.sun.j2me.app-descriptor",
    "text/vnd.wap.wml",
    "text/vnd.wap.wmlscript",
    "text/x-asm",
    "text/x-c",
    "text/x-fortran",
    "text/x-java-source,java",
    "text/x-pascal",
    "text/x-setext",
    "text/x-uuencode",
    "text/x-vcalendar",
    "text/x-vcard",
    "text/yaml",
    "image/vnd.djvu",
    "image/svg+xml"
])
