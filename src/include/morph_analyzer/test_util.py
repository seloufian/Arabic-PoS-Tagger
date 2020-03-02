import unittest

import util

WORD_LENGTH_LIMIT = 100

def _possible_lengths(wordlen):
    """Determine all possible suffix, stem, prefix lengths for the given
    word length."""
    results = set()

    for pre in range(util.MAX_PREFIX_LENGTH + 1):
        for suf in range(util.MAX_SUFFIX_LENGTH + 1):
            stem = wordlen - pre - suf
            if stem < 1:
                continue
            results.add((pre, stem, suf))

    return results

class TestUtil(unittest.TestCase):

    def _check_segment_limits(self, stem_idx, suf_idx, wordlen):
        prelen = stem_idx
        stemlen = suf_idx - stem_idx
        suflen = wordlen - suf_idx
        self.assertLessEqual(prelen, util.MAX_PREFIX_LENGTH)
        self.assertGreaterEqual(stemlen, 1)
        self.assertLessEqual(suflen, util.MAX_SUFFIX_LENGTH)

    def test_segment_indexes_limits(self):
        """Check if all indexes are within limits."""
        for wordlen in range(WORD_LENGTH_LIMIT):
            for stem_idx, suf_idx in util.segment_indexes(wordlen):
                self._check_segment_limits(stem_idx, suf_idx, wordlen)

    def test_segment_indexes_values(self):
        """Check if all possible index values are being given."""
        for wordlen in range(WORD_LENGTH_LIMIT):
            possibilities = _possible_lengths(wordlen)

            for stem_idx, suf_idx in util.segment_indexes(wordlen):
                prelen = stem_idx
                stemlen = suf_idx - stem_idx
                suflen = wordlen - suf_idx
                indexes = (prelen, stemlen, suflen)
                self.assertIn(indexes, possibilities)
                possibilities.remove(indexes)

            self.assertSetEqual(possibilities, set())

if __name__ == '__main__':
    unittest.main()
