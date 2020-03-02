import unittest

from buckwalter import buck2uni, uni2buck

# Examples taken from T. F. Mitchell, Writing Arabic (Oxford, 1953)

arabic_words = {
    ">a*ina": "أَذِنَ", # m1.1
    "<ibnN": "إِبنٌ", # m1.2
    ">um~N": "أُمٌّ", # m1.3
    "maso>alatN": "مَسْأَلَتٌ", # m1.7
    "qaAma": "قَامَ", # m2.1
    "EaArN": "عَارٌ", # m2.2
    # TODO add more words
}

other_words = [
    "κατέβην χθὲς εἰς Πειραιᾶ",
    "Война и мир",
]

class TestBuckwalter(unittest.TestCase):

    def test_buck2uni(self):
        for buck, uni in arabic_words.items():
            self.assertEqual(uni, buck2uni(buck))

    def test_buck2uni_other(self):
        for word in other_words:
            self.assertEqual(word, buck2uni(word))

    def test_uni2buck(self):
        for buck, uni in arabic_words.items():
            self.assertEqual(buck, uni2buck(uni))

    def test_uni2buck_other(self):
        for word in other_words:
            self.assertEqual(word, uni2buck(word))

if __name__ == '__main__':
    unittest.main()
