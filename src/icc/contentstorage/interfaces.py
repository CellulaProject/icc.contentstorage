from zope.interface import Interface

class IDocumentStorge(object):
    """Document key-content storage interface.
    The Storage can only
    1. save a document (any bytes) under an sha256 integer ID;
    2. retrieve a document identified with an integer sha256 ID;
    3. delete it by the ID;
    4. check if a document exists;
    5. remove all records from the database.

    Transactions are supported with
    1. Begin transaction (begin);
    2. end transaction (commit);
    3. end transaction (abort).

    All the metadata is stored elsewhere.
    """

    def put(content):
        """Put a content in a storage.
        Returns a sha256 ID as an integer.
        """

    def get(sha256_id):
        """Returns a content stored under
        sha256_id key.
        Return the key.
        """

    def remove(sha256_id):
        """Deletes a document stored uder
        sha256_id key.
        Return the key.
        """

    def clear(sha256_id):
        """Removes all data from the storage.
        Returns None.
        """

    def resolve(sha256_id):
        """Check if the content exists under
        the supplied key.
        Return non empty sha256_id as hex digest if so,
        else return False.
        """

    def begin():
        """Begin a transaction.
        """

    def commit():
        """Commit current transaction.
        """

    def abort():
        """Abort current transaction.
        """
