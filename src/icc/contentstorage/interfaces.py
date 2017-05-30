from zope.interface import Interface, Attribute


class IContentStorage(Interface):
    """Document key-content storage interface.
    The Storage can only
    1. save a document (any bytes) under an
       murmur128_id integer ID, which is calculated from content given;
    2. retrieve a document identified with an murmur128_id sha256 ID;
    3. delete it by the ID;
    4. check if a document exists;
    5. remove all records from the database.

    Transactions are supported with
    1. Begin transaction (begin);
    2. end transaction (commit);
    3. end transaction (abort).

    All the metadata is stored elsewhere.
    """

    def put(content, id=None, features=None):
        """Put a content in a storage under `id`.
        if `id` is None calculate it form content by
        murmur3 algorithms.

        Returns a hex string key which the content was saved under.

        If `features` dictionary is supplied the
        storage can guess the compression algorithm, and
        this dictionary will be updated with some additional
        data.
        """

    def get(id):
        """Returns a content stored under
        id, which is probably
        murmur3 128 bit key reflecting the
        content to be returned.

        Returns the stored content.
        """

    def remove(id):
        """Deletes a document stored under id
        The parameter `id` is probably a
        murmur3 128 bit key.

        Return the key.
        """

    def clear():
        """Removes all data from the storage.
        Returns None.
        """

    def resolve(id):
        """Check if the content exists under
        the supplied `id` key.
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


class IFileSystemScanner(Interface):
    """Defines a interface for file system scanners,
    which recursively traverse the file system,
    find files from a set, and then loads their
    basic metadata.
    """

    locations = Attribute("Reference to id<->filename mapper")
    dirs = Attribute("Directory listing to be scanned")

    def scan(path_list=None, cb=None):
        """Scan `path_list` for files and send their
        metadata to stores.
        Call callback `cb` for each file.
        """

    def scan_path(path, cb=None):
        """Scan `path`'s subdirs for files, send their
        content to metadata store.
        Call callback `cb` for each file.
        """
