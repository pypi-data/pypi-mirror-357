import unittest
import codecs
from msx_charset import msx_charset


class TestMSXCharsetIntl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # テスト実行前にコーデックを登録
        codecs.register(msx_charset)

    def test_encode_decode_ascii(self):
        text = "Hello, World!"
        encoded = text.encode("msx-intl")
        decoded = encoded.decode("msx-intl")
        self.assertEqual(text, decoded)

    def test_encode_decode_accented_chars(self):
        text = "áéíóúàèìòùâêîôû"
        encoded = text.encode("msx-intl")
        decoded = encoded.decode("msx-intl")
        self.assertEqual(text, decoded)

    def test_encode_decode_graphic_chars(self):
        text = "☺☻♥♦♣♠"
        encoded = text.encode("msx-intl")
        decoded = encoded.decode("msx-intl")
        self.assertEqual(text, decoded)

    def test_encode_decode_mixed(self):
        text = "Hello, áéíóú!"
        encoded = text.encode("msx-intl")
        decoded = encoded.decode("msx-intl")
        self.assertEqual(text, decoded)

    def test_codec_registration(self):
        self.assertIsNotNone(codecs.lookup("msx-intl"))
        self.assertIsNotNone(codecs.lookup("msx_intl"))

    def test_encode_bytes_ascii(self):
        # ASCII文字のバイト列テスト
        text = "Hello!"
        expected = bytes([0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x21])
        encoded = text.encode("msx-intl")
        self.assertEqual(encoded, expected)

    def test_encode_bytes_accented(self):
        # アクセント付き文字のバイト列テスト
        text = "áé"
        expected = bytes([0xA0, 0x82])
        encoded = text.encode("msx-intl")
        self.assertEqual(encoded, expected)

    def test_encode_bytes_graphic(self):
        # グラフィック文字のバイト列テスト
        text = "☺☻"
        expected = bytes([0x01, 0x41, 0x01, 0x42])
        encoded = text.encode("msx-intl")
        self.assertEqual(encoded, expected)

    def test_encode_bytes_mixed(self):
        # 混合文字のバイト列テスト
        text = "Aá"
        expected = bytes([0x41, 0xA0])
        encoded = text.encode("msx-intl")
        self.assertEqual(encoded, expected)

    def test_encode_decode_currency(self):
        text = "£$¥"
        encoded = text.encode("msx-intl")
        decoded = encoded.decode("msx-intl")
        self.assertEqual(text, decoded)

    def test_incremental_decode(self):
        decoder = codecs.getincrementaldecoder("msx-intl")()
        expected = ""
        decoded = decoder.decode(bytes([0x01]))
        self.assertEqual(decoded, expected)

        expected = "☺"
        decoded = decoder.decode(bytes([0x41]))
        self.assertEqual(decoded, expected)


if __name__ == "__main__":
    unittest.main()
