import unittest

from html_character_entity_decoder import decode_entities, decode_entities_in_string


class TestNamedEntities(unittest.TestCase):
    def test_basic_amp(self):
        self.assertEqual(decode_entities("a &amp; b"), "a & b")

    def test_copy(self):
        self.assertEqual(decode_entities("&copy;"), "\u00a9")

    def test_multiple_named(self):
        self.assertEqual(decode_entities("&amp;&lt;&gt;"), "&<>")

    def test_named_with_text_between(self):
        self.assertEqual(decode_entities("x &amp; y &lt; z"), "x & y < z")

    def test_unknown_named_left_verbatim(self):
        self.assertEqual(decode_entities("foo &notarealentity; bar"), "foo &notarealentity; bar")

    def test_named_without_semicolon_left_verbatim(self):
        # Only entities terminated by ';' are recognised. A bare ``&amp`` is
        # intentionally not decoded — the regex requires the semicolon.
        self.assertEqual(decode_entities("a &amp b"), "a &amp b")


class TestNumericDecimal(unittest.TestCase):
    def test_decimal_amp(self):
        self.assertEqual(decode_entities("&#38;"), "&")

    def test_decimal_copy(self):
        self.assertEqual(decode_entities("&#169;"), "\u00a9")

    def test_decimal_surrounding_text(self):
        self.assertEqual(decode_entities("code &#65; code"), "code A code")

    def test_decimal_zero(self):
        self.assertEqual(decode_entities("&#0;"), "\x00")

    def test_decimal_max(self):
        self.assertEqual(decode_entities("&#1114111;"), chr(0x10FFFF))

    def test_decimal_too_large_left_verbatim(self):
        self.assertEqual(decode_entities("&#1114112;"), "&#1114112;")


class TestNumericHex(unittest.TestCase):
    def test_hex_lowercase(self):
        self.assertEqual(decode_entities("&#x26;"), "&")

    def test_hex_uppercase_prefix(self):
        self.assertEqual(decode_entities("&#X26;"), "&")

    def test_hex_uppercase_digits(self):
        self.assertEqual(decode_entities("&#x26;"), "&")

    def test_hex_a9(self):
        self.assertEqual(decode_entities("&#xa9;"), "\u00a9")

    def test_hex_mixed_case(self):
        self.assertEqual(decode_entities("&#xA9;"), "\u00a9")

    def test_hex_uppercase_x_prefix_lowercase_digits(self):
        self.assertEqual(decode_entities("&#Xa9;"), "\u00a9")

    def test_hex_too_large_left_verbatim(self):
        self.assertEqual(decode_entities("&#x110000;"), "&#x110000;")


class TestNoEntities(unittest.TestCase):
    def test_plain_text(self):
        self.assertEqual(decode_entities("just text"), "just text")

    def test_empty_string(self):
        self.assertEqual(decode_entities(""), "")

    def test_amp_with_no_entity(self):
        # No semicolon, no match — left verbatim.
        self.assertEqual(decode_entities("this & that"), "this & that")

    def test_lone_amp_at_end(self):
        self.assertEqual(decode_entities("ends with &"), "ends with &")


class TestNonInterference(unittest.TestCase):
    def test_entity_result_not_redecoded(self):
        # ``&amp;#38;`` decodes the ``&amp;`` to ``&``. The result ``&#38;``
        # is NOT re-decoded to ``&``. This is the single-pass semantics.
        self.assertEqual(decode_entities("&amp;#38;"), "&#38;")

    def test_double_amp(self):
        # Both ``&amp;`` and ``&#38;`` appear in the original input and are
        # decoded in a single pass. Neither is a product of decoding the other.
        self.assertEqual(decode_entities("&amp;&#38;"), "&&")

    def test_existing_plain_amp_not_touched(self):
        self.assertEqual(decode_entities("& &amp; &"), "& & &")


class TestTypeContract(unittest.TestCase):
    def test_returns_str(self):
        self.assertIsInstance(decode_entities(""), str)

    def test_alias_is_same_function(self):
        self.assertIs(decode_entities_in_string, decode_entities)

    def test_type_error_on_non_string(self):
        with self.assertRaises(TypeError):
            decode_entities(123)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
