from icc.contentstorage.interfaces import IDocumentStorage
from zope.interface import implementer
import hashlib

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
class DictionaryDocStorage(object):
    """Stores content in a kyotocabinet cool DBM.
    """

    def __init__(self):
        self.clear()

    def clear(self):
        """Removes all records in the storage.
        """
        self.docs={}
        self.transact=None

    def put(self, content):
        m=hashlib.sha256()
        m.update(content)
        key=m.digest()
        self.docs[key]=content
        return hexdigest(key)

    def get(self, key):
        if type(key)==StringType:
            key=bindigest(key)
        return self.docs[key]

    def remove(self, key):
        key=self.resolve(key)
        del self.docs[key]

    def resolve(self, key):
        if type(key)==str:
            key=bindigest(key)
        if key in self.docs:
            return key
        return False

    def begin(self): # FIXME: Does this affect to a throughoutput?
        pass

    def commit(self):
        self.transact=None

    def abort(self):
        self.transact=None
