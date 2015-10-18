"""
from zope.configuration.xmlconfig import xmlconfig
from pkg_resources import resource_stream, resource_string

package=__name__

#config_file=resource_stream(package, "application.ini")
# xmlconfig(resource_stream(package, "configure.zcml"))

xmlconfig(resource_stream(package, "configure.zcml"))
"""

from icc.contentstorage.interfaces import IDocumentStorage
from zope.interface import implementer
import hashlib
from kyotocabinet import DB
import os

def hexdigest(digest):
    """Convert byte digest to
    hex digest
    Arguments:
    - `digest`: Byte array representing
    digest
    """
    return ''.join(["{:02x}".format(b) for b in d])

def bindigest(digest):
    return bytearray.fromhex(digest)

@implementer(IDocumentStorage)
class KiotoCabinetDocStorage(object):
    """Stores content in a kyotocabinet cool DBM.
    """

    def __init__(self, filename):
        """Opens a storage file and start serve as a
        module.

        Arguments:
        - `filename`: Preferrably full path location
        of the file where content is to be stored.
        """
        assert not filename.endswith('.kch') or not filename.endswith('.KCH'), 'wrong extension'
        self._filename = filename
        self.open(self._filename)

    def open(self, filename):
        self.db=DB()
        if not self.db.open(filename, DB.OWRITER | DB.OCREATE):
            raise IOError("open error: '" + str(self.db.error())+"' on file:" + filename)

    def clear(self):
        """Removes all records in the storage.
        """
        self.db.clear()

    def put(self, content):
        m=hashlib.sha256()
        m.update(content)
        key=m.digest()
        self.db.set(key, content)
        return hexdigest(key)

    def get(self, key):
        """Returns a content stored under
        the supplied key.

        Arguments:
        - `key`: Key of a content to be deleted.
        """
        if type(key)==StringType:
            key=bindigest(key)
        if not self.db.resolve(key):
            raise KeyError('wrong key')
        return self.db.get(key)

    def remove(self, key):
        """Removes a content stored under
        the supplied key

        Arguments:
        - `key`: Key of a content to be deleted.
        """

        key=self.resolve(key)
        if not key :
            raise KeyError('wrong key')
        return key

    def resolve(self, key):
        """Figure out a content existence stored
        under the supplied key.

        Arguments:
        - `key`: Key of a content to be checked.
        """
        if type(key)==str:
            key=bindigest(key)
        if self.db.resolve(key):
            return key
        return False

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
