from icc.contentstorage.interfaces import IContentStorage
from zope.interface import implementer, Interface
from kyotocabinet import DB
import os
import os.path
#from pathlib import Path
from icc.contentstorage import hexdigest, intdigest, hash128_int
from icc.contentstorage import COMP_EXT, COMP_MIMES
from zope.component import getUtility
import zlib

import logging
logger = logging.getLogger("icc.contentstorage")


@implementer(IContentStorage)
class KyotoCabinetDocStorage(object):
    """Stores content in a kyotocabinet cool DBM.
    """

    def __init__(self,
                 filename,
                 pathname,
                 zlib_level=6,
                 size_tr=50 * 1024 * 1024,
                 filepaths=None,
                 storage_name=None
                 ):
        """Opens a storage file and start serve as a
        module.
        Do not compress file of size > size_tr (50 Mb by default)
        implying them to be a multimedia.

        Arguments:
        - `path`: Preferably full path location
        of the file `filename` where content is to be indexed.
        - `filepaths`: Path where file data is being found and scanned.
        """
        assert not filename.endswith('.kch') or not filename.endswith(
            '.KCH'), 'wrong extension'
        self._filename = os.path.join(pathname, filename)
        self.pathname = pathname
        self.filename = filename
        if zlib_level > 9:
            zlib_level = 9
        if zlib_level < 0:
            zlib_level = 0
        self.zlib_level = zlib_level
        self.size_tr = size_tr
        self.storage_name = storage_name
        self.db = self.open(self._filename)

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

    def put(self, content, id=None, features=None):
        key = int_digest = intdigest(self._hash(content))
        if id is not None:
            key = id
        compressed = False
        org_size = len(content)
        if features is not None:
            for mk in ["Content-Type", "mimetype", "mime-type", "Mime-Type"]:
                if mk in features:
                    md = features[mk]
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
                    filename = features.get("File-Name", None)
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
                logger.info(
                    "STORAGE: Compressed size is bigger, than original.")
        rc = self.db.set(key, content)
        if not rc:
            raise RuntimeError(
                "could not store the content: {}".self.db.error())
        if features is not None:
            hex_digest = hexdigest(int_digest)
            new_md["nfo:hashValue"] = hex_digest
            if new_md:
                features.update(new_md)

        return key

    def get(self, key):
        """Returns a content stored under
        the supplied key.

        Arguments:
        - `key`: Key of a content to be deleted.
        """
        key = intdigest(key)

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

    def initialize(self):
        pass


class Storage(KyotoCabinetDocStorage):

    def __init__(self, prefix="content"):
        """Initializes with a calue from an .ini section.
        [${`prefix`}_storage]
        datapath="/home/eugeneai/tmp/cellula-data/content.kch"
        """

        config = getUtility(Interface, name='configuration')

        section_name = '{}_storage'.format(prefix)

        conf = config[section_name]

        filename = conf['file']
        pathname = conf['path']
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

        pathname = os.path.abspath(pathname)
        dirname = pathname  # os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        zlib_level = conf.get('zlib_level', 6)
        size_tr = conf.get('size', 50)
        size_tr = int(size_tr) * 1024 * 1024
        filename = filename.strip("'").strip('"')

        storage_name = prefix

        KyotoCabinetDocStorage.__init__(
            self,
            filename,
            pathname,
            zlib_level=zlib_level,
            size_tr=size_tr,
            filepaths=dirs,
            storage_name=storage_name
        )


class LocationStorage(Storage):

    def __init__(self, prefix="locations"):
        super(LocationStorage, self).__init__(prefix)


class ReadOnlyStorage(Storage):

    def open(self, filename):
        db = DB()
        if not db.open(filename, DB.OREADER | DB.ONOLOCK):
            raise IOError("open error: '" + str(self.db.error()) + "' on file:"
                          + filename)
        return db
