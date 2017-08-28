from icc.contentstorage.interfaces import IContentStorage, IFileSystemScanner
from zope.interface import implementer, Interface
import os
import os.path
from icc.contentstorage import hexdigest, hash128_int, bindigest
from zope.component import getUtility
from icc.contentstorage import GOOD_EXT

import logging
logger = logging.getLogger("icc.contentstorage")


@implementer(IFileSystemScanner, IContentStorage)
class FileSystemScanner(object):
    """Stores content in a kyotocabinet cool DBM.
    """

    def __init__(self,
                 content_storage="content",
                 location_storage="locations",
                 dirs=None,
                 storage_name=None
                 ):

        self.content_storage = content_storage
        self.location_storage = location_storage
        self.dirs = dirs
        self.initialized = False
        self.storage_name = storage_name

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

    def clear(self):
        """Removes all records in the storage.
        """
        self.content_storage.clear()
        self.location_storage.clear()

    def hash(self, content):
        return hexdigest(self._hash(
            content))  # NOTE: Digest for original non-compressed content.

    def _hash(self, content):
        return hash128_int(content)

    def put(self, content, id=None, features=None):
        return self.content_storage.put(content=content,
                                        id=id, features=features)

    def resolve_location(self, id):
        id = bytes(bindigest(id))
        loc_key = self.location_storage.resolve(id)
        logger.debug(
            "RL:Resolve location: {}->'{}'".format(hexdigest(id), loc_key))
        if loc_key:
            return loc_key, self.location_storage.get(id).decode('utf-8')
        else:
            return False, None

    def get(self, id):
        loc_key, pathname = self.resolve_location(id)
        if loc_key:
            with open(pathname, "rb") as inp:
                return inp.read()  # FIXME: size_tr?
        else:
            return self.content_storage.get(id)

    def remove(self, id):
        loc_key, pathname = self.resolve_location(id)
        if loc_key:
            self.location_storage.remove(id)
            self.location_storage.remove(pathname)
        return self.content_storage.remove(id)

    def resolve(self, id):
        loc_key, _ = self.resolve_location(id)
        if loc_key:
            return loc_key
        return self.content_storage.resolve(id)

    def begin(self, hard=True):
        self.location_storage.begin()
        self.content_storage.begin()

    def commit(self):
        self.content_storage.commit()
        self.location_storage.commit()

    def abort(self):
        self.content_storage.abort()
        self.location_storage.abort()

    def scan_directories(self, cb=None, scanonly=False, count=None):
        c = 0
        new = 0
        for fp in self.dirs:
            dcount, dnew = self.scan_path(
                fp, cb=cb, scanonly=scanonly, count=count)
            c += dcount
            new += dnew
            if count is not None:
                count -= dcount
                if count <= 0:
                    break
        return c, new

    def scan_path(self, path, cb=None, scanonly=False, count=None):
        c = new = 0
        logger.info("SCAN:Start scanning: {}".format(path))
        for dirpath, dirnames, filenames in os.walk(path):
            if count is not None and count <= 0:
                break
            for filename in filenames:
                if filename[0] in ["."]:
                    continue
                c += 1
                if count is not None:
                    if count <= 0:
                        break
                    count -= 1
                fullfn = os.path.join(dirpath, filename)
                filen, ext = os.path.splitext(filename)
                ext = ext.lower()

                print("SCAN:{} ext: {}".format(filen, ext))
                if ext not in GOOD_EXT:
                    if cb is not None:
                        cb("start", fullfn, filename,
                           count=c, new=True, good=False)
                    continue

                # FIXME: Use relative paths for file name -> key mapping.
                fnkey = fullfn  # FIXME case insensitivity
                hfnkey = self._hash(fnkey)
                # print("fnkey:", fnkey, self.locs.check(fnkey))
                if self.location_storage.resolve(hfnkey):
                    # The file does exist in the location storage.
                    if cb is not None:
                        cb("start", fullfn, filename,
                           count=c, new=None, good=True)
                    continue

                if scanonly:
                    if cb is not None:
                        new += 1
                        cb("start", fullfn, filename,
                           count=c, new=new, good=True)
                    continue

                rc = self.processfile(fullfn)
                if rc:
                    new += 1
                    if cb is not None:
                        cb("end", fullfn, filename, count=c,
                           new=new, good=True)
                else:
                    if cb is not None:
                        cb("end", fullfn, filename, count=c,
                           new=False, good=True)

        logger.info("SCAN:Scanning finished with count={} and new={}".format(
            c, new))
        return c, new

    def processfile(self, filename, features=None):

        fnkey = filename  # FIXME case insensitivity
        hfnkey = self._hash(fnkey)

        size_tr = self.content_storage.size_tr
        with open(filename, "rb") as infile:
            key = self._hash(infile.read(size_tr))
            logger.debug("Inside process {}, {}".format(filename, features))
            hk = features["id"] = hexdigest(key)
            hkb = bytes(bindigest(hk))
            fna = filename.encode("utf-8")
            logger.debug("FN:{}=={}".format(filename, fna))
            assert filename == fna.decode("utf-8")
            oldloc, okey = self.resolve_location(key)
            if oldloc:
                # A duplicate happened
                return okey
            self.location_storage.put(fna, id=key)
        return key


def initialize_subscriber(event):
    from icc.cellula import default_storage
    default_storage().initialize()


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
            dirs=dirs,
            storage_name=prefix
        )
