from icc.contentstorage import (
    bindigest,
    hexdigest,
    intdigest,
    hash128_int
)
import os
import pprint
import itertools

BYTES = os.urandom(1024 * 1024)

funcs = set([
    bindigest,
    hexdigest,
    intdigest
])


class TestBasics:
    def test_test(self):
        assert True

    def test_bd(self):
        assert bindigest(BYTES)

    def test_conbs(self):
        l = set()
        h128 = hash128_int(BYTES)
        for a, b in itertools.product(funcs, funcs):
            l.add(hexdigest(a(h128)))
            assert a(h128) == a(b(h128))
            print("Run on {} and {}".format(a, b))
        pprint.pprint(l)
        assert len(l) == 1
