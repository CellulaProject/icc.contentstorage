from icc.contentstorage.interfaces import IContentStorage, IFileSystemScanner
from zope.interface import implementer, Interface
import os
import os.path
from icc.contentstorage import hexdigest, intdigest, hash128_int
from zope.component import getUtility

import logging
logger = logging.getLogger("icc.contentstorage")


@implementer(IFileSystemScanner, IContentStorage)
class FileSystemScanner(object):
    """Stores content in a kyotocabinet cool DBM.
    """

    def __init__(self,
                 content_storage="content",
                 location_storage="locations",
                 dirs=None):

        self.content_storage = content_storage
        self.location_storage = location_storage
        self.dirs = dirs
        self.initialized = False

    def initialize(self):
        if self.initialized:
            return

        if isinstance(self.content_storage, str):
            self.content_storage = getUtility(
                IContentStorage, self.content_storage)
        if isinstance(self.location_storage, str):
            self.location_storage = getUtility(
                IContentStorage, self.location_storage)

        self.initialized = True

    def open(self, filename):
        db = DB()

        # self.db=DB(DB.GEXCEPTIONAL)
        if not db.open(filename, DB.OWRITER | DB.OCREATE | DB.ONOLOCK):
            raise IOError("open error: '" + str(self.db.error()) + "' on file:"
                          + filename)
        return db

    def clear(self):
        """Removes all records in the storage.
        """
        self.db.clear()

    def hash(self, content):
        return hexdigest(self._hash(
            content))  # NOTE: Digest for original non-compressed content.

    def _hash(self, content):
        return hash128_int(content)

    def put(self, content, metadata=None):
        key = intdigest(self._hash(content))
        compressed = False
        org_size = len(content)
        if metadata is not None:
            for mk in ["Content-Type", "mimetype", "mime-type", "Mime-Type"]:
                if mk in metadata:
                    md = metadata[mk]
                    mdl = md
                    if type(mdl) != list:
                        mdl = [mdl]
                    for md_ in mdl:
                        if md_.find('compressed') >= 0:
                            compressed = True
                            break
                        if md_ in COMP_MIMES:
                            compressed = True
                            break
                    if compressed:
                        break
                    filename = metadata.get("File-Name", None)
                    if filename:
                        for ext in COMP_EXT:
                            if filename.endswith(ext):
                                compressed = True
                                break
                    logger.debug("STORAGE got mime(s):" + str(md))

        # c_key=key << 8
        new_md = {}
        if not compressed and len(
                content) <= self.size_tr and self.zlib_level > 0:
            #            if type(content)==str:
            #                content=content.encode("")
            new_content = zlib.compress(content, self.zlib_level)
            if len(content) > len(new_content):
                content = new_content
                new_md['nfo:uncompressedSize'] = org_size
            else:
                logger.info("STORAGE: Compressed is bigger, than original.")
        self.db.set(key, content)
        if new_md:
            metadata.update(new_md)
        return hexdigest(key)

    def get(self, key):
        """Returns a content stored under
        the supplied key.

        Arguments:
        - `key`: Key of a content to be deleted.
        """
        key = intdigest(key)

        if self.locs.check(key) >= 0:
            return self._get_from_dirs(key)

        c_key = self.resolve_compressed(key)
        logger.debug("PhysKey: %d" % c_key)
        content = self.db.get(c_key)
        if content is None:
            return None
        if content[:2] == b'x\x9c':
            try:
                content = zlib.decompress(content)
            except zlib.error:
                pass  # Not a compressed format
        loaded_hash = self.hash(content)
        stored_hash = hexdigest(key)
        if (loaded_hash != stored_hash):
            logger.error("Hashes are different!")
        else:
            logger.info("Hashes are ok! %s" % loaded_hash)
        return content

    def _get_from_dirs(self, key):
        filename = self.locs.get(key)
        content = open(filename, "rb").read()
        return content

    def remove(self, key):
        """Removes a content stored under
        the supplied key

        Arguments:
        - `key`: Key of a content to be deleted.
        """

        c_key = self.resolve_compressed(key)
        self.db.remove(c_key)
        return hexdigest(key)

    def resolve(self, key):
        """Figure out a content existence stored
        under the supplied key.

        Arguments:
        - `key`: Key of a content to be checked.
        """

        c_key = self.resolve_compressed(key, no_raise=True)
        if c_key is False:
            return False
        return key

    def resolve_compressed(self, key, no_raise=False):
        """Resolve compression bit in key. (?)
        if file is compressed, then return
        Arguments:
        - `key`:
        """
        key = intdigest(key)
        if self.db.check(key) >= 0:
            return key
        if no_raise:
            return False
        raise KeyError("no content for key: " + hexdigest(key))

    def begin(self, hard=True):
        # FIXME: Does this affect the throughoutput?
        """Begin a transaction.

        Arguments:
        - hard: a Boolean value. True value denotes
        respect physical synchronization.
        """
        self.db.begin_transaction(hard)

    def commit(self):
        """Commit a transaction.
        """
        self.db.end_transaction(True)

    def abort(self):
        """Commit a transaction.
        """
        self.db.end_transaction(False)

    def scan_directories(self, cb=None):
        count = 0
        new = 0
        for fp in self.filepaths:
            dcount, dnew = self.scan_path(fp, cb=cb)
            count += dcount
            new += dnew
        return count, new

    def scan_path(self, path, cb=None):
        count = new = sync = 0
        sync_size = [10, 50]
        print("Start scanning: {}".format(path))
        for dirpath, dirnames, filenames in os.walk(path):
            # for filename in [f for f in filenames if f.endswith(".log")]:
            for filename in filenames:
                if filename[0] in ["."]:
                    continue
                count += 1
                fullfn = os.path.join(dirpath, filename)
                if cb is not None:
                    cb("start", fullfn, count=count, new=None)
                fnkey = fullfn + "#FN"  # FIXME case insensitivity
                hfnkey = self._hash(fnkey)
                # print("fnkey:", fnkey, self.locs.check(fnkey))
                if self.locs.check(hfnkey) >= 0:
                    continue
                # print("her")
                with open(fullfn, "rb") as infile:
                    key = self._hash(infile.read(self.size_tr))
                    if self.locs.check(key) >= 0:
                        # A duplicate happened
                        continue
                    self.locs.set(key, fullfn)
                    self.locs.set(hfnkey, key)
                    sync += 1
                    for n, ss in enumerate(sync_size):
                        if sync % ss == 0:
                            self.locs.synchronize(n)
                    new += 1
                if cb is not None:
                    cb("end", fullfn, count=count, new=new)
        return count, new

    def _init(self):
        pass


class ScannerStorage(FileSystemScanner):

    def __init__(self, prefix="scanner"):
        """Initializes with a calue from an .ini section.
        [content_scanner]
        content_storage=content
        location_storage=locations
        dirs=...:....:...:....
        """

        config = getUtility(Interface, name='configuration')

        conf = config['{}_storage'.format(prefix)]

        content_s = conf.get('content_storage', "content")
        location_s = conf.get('location_storage', "locations")
        dirs = conf.get('dirs', None)
        if dirs:
            dirs = dirs.split(":")
            ndirs = []
            for d in dirs:
                d = os.path.abspath(d)
                if not os.path.isdir(d):
                    raise RuntimeError("{} not a directory".format(d))
                ndirs.append(d)
        dirs = ndirs

        super(self.__class__, self).__init__(
            content_storage=content_s,
            location_storage=location_s,
            dirs=dirs)
