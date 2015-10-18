from icc.contentstorage.interfaces import IDocumentStorage
from zope.interface import implementer
import hashlib
from kyototycoon import KyotoTycoon
import os
from icc.contentstorage import hexdigest,bindigest

@implementer(IDocumentStorage)
class KiotoTycoonDocStorage(object):
    """Stores content in on a kyototycoon server.
    """

    def __init__(self, host="127.0.0.1", port=11978):
        self.connection={'host':host, 'port':port}
        self.connect(**connection)

    def connect(self, **kwargs):
        self.conn=KyotoTycoon(binary=True)
        if not self.conn.open(**kwargs):
            self.raise RuntimeError('cannot connect to server')

    def clear(self):
        """Removes all records in the storage.
        """
        self.conn.clear()

    def put(self, content):
        m=hashlib.sha256()
        m.update(content)
        key=m.digest()
        self.conn.set(key, content)
        return hexdigest(key)

    def get(self, key):
        """Returns a content stored under
        the supplied key.

        Arguments:
        - `key`: Key of a content to be deleted.
        """
        key=self.resolve(key):
        return self.conn.get(key)

    def remove(self, key):
        """Removes a content stored under
        the supplied key

        Arguments:
        - `key`: Key of a content to be deleted.
        """

        key=self.resolve(key)
        self.conn.remove(key)
        return key

    def resolve(self, key):
        """Figure out a content existence stored
        under the supplied key.

        Arguments:
        - `key`: Key of a content to be checked.
        """
        if type(key)==str:
            key=bindigest(key)
        if self.db.check(key):
            return key
        return False

    def begin(self): # FIXME: Does this affect to a throughoutput?
        pass

    def commit(self):
        pass

    def abort(self):
        pass
