"""
from zope.configuration.xmlconfig import xmlconfig
from pkg_resources import resource_stream, resource_string

package=__name__

#config_file=resource_stream(package, "application.ini")
# xmlconfig(resource_stream(package, "configure.zcml"))

xmlconfig(resource_stream(package, "configure.zcml"))
"""

from icc.contentstorage.interfaces import IDocumentStorage
from zope.interface import implementer, Interface
from kyotocabinet import DB
import os
from icc.contentstorage import hexdigest,intdigest,hash128_int
from zope.component import getUtility
import zlib

COMP_MIMES=set([ # https://en.wikipedia.org/wiki/List_of_archive_formats
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
    ])

COMP_EXT=set([
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
    # FIXME Add more
    ])

@implementer(IDocumentStorage)
class KyotoCabinetDocStorage(object):
    """Stores content in a kyotocabinet cool DBM.
    """

    def __init__(self, filename, zlib_level=6, size_tr=50*1024*1024):
        """Opens a storage file and start serve as a
        module.
        Do not compress file of size > size_tr (50 Mb by default)
        implying them a multimedia.

        Arguments:
        - `filename`: Preferrably full path location
        of the file where content is to be stored.
        """
        assert not filename.endswith('.kch') or not filename.endswith('.KCH'), 'wrong extension'
        self._filename = filename
        if zlib_level>9:
            zlib_level=9
        if zlib_level<0:
            zlib_level=0
        self.zlib_level=zlib_level
        self.size_tr=size_tr
        self.open(self._filename)

    def open(self, filename):
        self.db=DB()
        if not self.db.open(filename, DB.OWRITER | DB.OCREATE):
            raise IOError("open error: '" + str(self.db.error())+"' on file:" + filename)

    def clear(self):
        """Removes all records in the storage.
        """
        self.db.clear()

    def put(self, content, metadata=None):
        key=hash128_int(content)   # NOTE: Digest for original content.
        compressed=False
        if metadata != None:
            for mk in ["Content-Type", "mimetype", "mime-type", "Mime-Type"]:
                if mk in metadata:
                    md=metadata[mk]
                    if md.find('comressed')>=0:
                        compressed=True
                        break
                    if md in COMP_MIMES:
                        compressed=True
                        break
                    filename=metadata.get("File-Name", None)
                    if filename:
                        for ext in COMP_EXT:
                            if filename.endswith(ext):
                                compressed=True
                                break
                    print ("STORAGE got mime:", md)

        c_key=key << 8
        if not compressed and len(content)<=self.size_tr and self.zlib_level>0:
#            if type(content)==str:
#                content=content.encode("")
            new_content=zlib.compress(content, self.zlib_level)
            if len(content) > len(new_content):
                content=new_content
                c_key|=1
            else:
                print ("STORAGE: Compressed is bigger, than original.")
        self.db.set(c_key, content)
        return hexdigest(key)

    def get(self, key):
        """Returns a content stored under
        the supplied key.

        Arguments:
        - `key`: Key of a content to be deleted.
        """
        c_key,compressed=self.resolve_compressed(key)
        content=self.db.get(c_key)
        if compressed:
            content=zlib.decompress(content)
        return content

    def remove(self, key):
        """Removes a content stored under
        the supplied key

        Arguments:
        - `key`: Key of a content to be deleted.
        """

        c_key, compressed=self.resolve_compressed(key)
        self.db.remove(c_key)
        return hexdigest(key)

    def resolve(self, key):
        """Figure out a content existence stored
        under the supplied key.

        Arguments:
        - `key`: Key of a content to be checked.
        """
        c_key, compressed = self.resolve_compressed(key, no_raise=True)
        if c_key==False:
            return False
        return key

    def resolve_compressed(self, key, no_raise=False):
        """Resolve compression bit in key.
        if file is compressed, then return
        Arguments:
        - `key`:
        """
        key=intdigest(key)
        nc_key=key << 8     # A lot of bits can be used to store flags.
        cc_key=nc_key | 1
        if self.db.check(cc_key):
            return cc_key, True
        if self.db.check(nc_key):
            return nc_key, False
        if no_raise:
            return False, False
        raise ValueError("no content for key")

    def begin(self, hard=True): # FIXME: Does this affect to a throughoutput?
        """Begin a transaction.

        Arguments:
        - hard: a Boolean value. True value denotes
        respect physical synchronisation.
        """
        self.db.begin_transation(hard=hard)

    def commit(self):
        """Commit a transaction.
        """
        self.db.end_transaction(commit=True)

    def abort(self):
        """Commit a transaction.
        """
        self.db.end_transaction(commit=False)

class Storage(KyotoCabinetDocStorage):
    def __init__(self, ):
        """Initializes with a calue from an .ini section.
        [content_storage]
        datapath="/home/eugeneai/tmp/cellula-data/content.kch"
        """

        config=getUtility(Interface, name='configuration')

        filename = config['content_storage']['file']
        zlib_level = config['content_storage'].get('zlib_level',6)
        size_tr = config['content_storage'].get('size_tr',50*1024*1024)
        filename=filename.strip("'").strip('"')

        KyotoCabinetDocStorage.__init__(self, filename, zlib_level=zlib_level, size_tr=size_tr)
