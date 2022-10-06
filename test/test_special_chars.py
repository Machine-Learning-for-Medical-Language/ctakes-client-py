import unittest
import ctakesclient

class TestSpecialChars(unittest.TestCase):
    """
    Test OPTIONAL encodings (UTF8 or ASCII) -- ctakes client and server not assuming the needs of the user.
    Note that dropping characters from the original physician note can change "MatchText.span()".
    """
    def test_unicode(self):
        """
        https://stackoverflow.com/questions/34618149/post-unicode-string-to-web-service-using-python-requests-library
        """
        text = ctakesclient.client.utf8("Två dagar kvar🎉🎉")
        escaped = b'Tv\xc3\xa5 dagar kvar\xf0\x9f\x8e\x89\xf0\x9f\x8e\x89'

        self.assertEqual(text, escaped)
        self.assertEqual(len(text), len(escaped))

    def test_ascii(self):
        """
        https://pythonguides.com/remove-unicode-characters-in-python/#:~:text=In%20python%2C%20to%20remove%20non,decode().
        """
        string_nonASCII = " àa fuünny charactersß. "
        string_encode = string_nonASCII.encode("ascii", "ignore")
        string_decode = string_encode.decode()
        expected = ' a funny characters. '
        self.assertEqual(expected, string_decode)
        self.assertEqual(expected, ctakesclient.client.ascii(string_nonASCII).decode())


if __name__ == '__main__':
    unittest.main()
