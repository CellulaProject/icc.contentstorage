from zope.interface import Interface

class IDocumentStorage(Interface):
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

    def put(content, metadata_dictionary):
        """Put a content in a storage.
        Returns a murmur3 128 bit ID as hex string.
        If metadat_dictioary is supplied the
        storage can guess wether or not to compress
        data.
        """

    def get(murmur128_id):
        """Returns a content stored under
        murmur3 128 bit key.
        Returns the stored content.
        """

    def remove(murmur128_id):
        """Deletes a document stored uder
        murmur3 128 bit key.
        Return the key.
        """

    def clear():
        """Removes all data from the storage.
        Returns None.
        """

    def resolve(murmur128_id):
        """Check if the content exists under
        the supplied key.
        Return non empty key as integer digest if so,
        otherwise return False.
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
