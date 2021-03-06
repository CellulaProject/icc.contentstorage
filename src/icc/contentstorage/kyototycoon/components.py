from icc.contentstorage.interfaces import IContentStorage
from zope.interface import implementer
import hashlib
from kyototycoon import KyotoTycoon
import os
from icc.contentstorage import hexdigest,bindigest

@implementer(IContentStorage)
class KiotoTycoonDocStorage(object):
    """Stores content in on a kyototycoon server.
    """

    def __init__(self, host="127.0.0.1", port=11978):
        self.connect(host=host,port=port)

    def connect(self, **kwargs):
        self.conn=KyotoTycoon(binary=False)
        self.conn.open(**kwargs)

    def clear(self):
        """Removes all records in the storage.
        """
        self.conn.clear()

    def put(self, content):
        m=hashlib.sha256()
        m.update(content)
        key=m.hexdigest()
        self.conn.set(key, content)
        return key

    def get(self, key):
        """Returns a content stored under
        the supplied key.

        Arguments:
        - `key`: Key of a content to be deleted.
        """
        key=self.resolve(key)
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
        if type(key)!=str:
            key=hexdigest(key)
        if self.conn.check(key):
            return key
        raise KeyError("no such key")

    def begin(self): # FIXME: Does this affect to a throughoutput?
        pass

    def commit(self):
        pass

    def abort(self):
        pass
