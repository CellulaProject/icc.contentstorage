from icc.contentstorage.interfaces import IContentStorage, IFileSystemScanner
from zope.interface import implementer, Interface
import os
import os.path
from icc.contentstorage import hexdigest, hash128_int
from zope.component import getUtility
from icc.contentstorage import COMP_EXT

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

    def put(self, content, metadata=None):
        return self.content_storage.put(content=content, metadata=metadata)

    def get(self, id):
        return self.content_storage.get(id)

    def _get_from_dirs(self, key):
        filename = self.locs.get(key)
        content = open(filename, "rb").read()
        return content

    def remove(self, id):
        self.location_storage.remove(id)  # FIXME: Remove backward reference
        return self.content_storage.remove(id)

    def resolve(self, id):
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

    def scan_directories(self, cb=None, scanonly=False):
        count = 0
        new = 0
        for fp in self.dirs:
            dcount, dnew = self.scan_path(fp, cb=cb, scanonly=scanonly)
            count += dcount
            new += dnew
        return count, new

    def scan_path(self, path, cb=None, scanonly=False):
        count = new = 0
        logger.info("Start scanning: {}".format(path))
        for dirpath, dirnames, filenames in os.walk(path):
            # for filename in [f for f in filenames if f.endswith(".log")]:
            for filename in filenames:

                if filename[0] in ["."]:
                    continue

                count += 1
                fullfn = os.path.join(dirpath, filename)

                ext = os.path.splitext(filename)

                if ext not in COMP_EXT:
                    if cb is not None:
                        cb("start", fullfn, filename, count=count, new=None)

                # FIXME: Use relative paths for file name -> key mapping.
                fnkey = fullfn  # FIXME case insensitivity
                hfnkey = self._hash(fnkey)
                # print("fnkey:", fnkey, self.locs.check(fnkey))
                if self.location_storage.resolve(hfnkey):
                    # The file does exist in the location storage.
                    if cb is not None:
                        cb("start", fullfn, filename, count=count, new=None)
                    continue

                if scanonly:
                    if cb is not None:
                        new += 1
                        cb("start", fullfn, filename, count=count, new=new)
                    continue

                rc = self.processfile(fullfn)
                if rc:
                    new += 1
                    if cb is not None:
                        cb("end", fullfn, filename, count=count, new=new)
                else:
                    if cb is not None:
                        cb("end", fullfn, filename, count=count, new=False)

        return count, new

    def processfile(self, filename, features=None):

        fnkey = filename  # FIXME case insensitivity
        hfnkey = self._hash(fnkey)

        size_tr = self.content_storage.size_tr
        with open(filename, "rb") as infile:
            key = self._hash(infile.read(size_tr))
            logger.debug("Inside process {}, {}".format(filename, features))
            return key
            self.location_storage.set(key, filename)
            self.location_storage.set(hfnkey, key)
            if self.location_storage.resolve(key):
                # A duplicate happened
                return False
            # for n, ss in enumerate(sync_size):
            #     if sync % ss == 0:
            #         # FIXME: Only for kyotucabinet.
            #         self.location_storage.db.synchronize(n)

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
            dirs=dirs)
