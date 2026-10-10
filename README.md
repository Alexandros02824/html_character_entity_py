# HTML Character Entity Decoder

Decodes HTML character entities — named (``&amp;``), decimal numeric
(``&#38;``), and hex numeric (``&#x26;``) — to their Unicode characters.

```python
from html_character_entity_decoder import decode_entities

decode_entities("Tom &amp; Jerry &#38; &#x26; copy")
# -> 'Tom & Jerry & & copy'
```

## Why

You have strings with HTML entities and want plain text back. The standard
library ships ``html.unescape``, but its behaviour on malformed input is not
obvious from its name and it carries the full entity map in memory whether
you need it or not. This library is a thin, explicit wrapper around the
``html.entities.html5`` name table and a single regex; it says plainly what
it decodes and what it leaves alone.

## Edge cases you will hit

Entities are decoded **exactly once**. ``&amp;#38;`` becomes ``&#38;``, not
``&`` — the entity produced by decoding is not itself re-decoded. This matches
what browsers do in plain-text contexts (script, textarea). If you need
repeated unescaping until a fixpoint, call the function in a loop and stop
when the output stops changing.

Only entities terminated by a semicolon are recognised. ``&amp`` without the
``;`` is left verbatim. Unknown named entities and numeric references outside
the valid Unicode range (``0``–``0x10FFFF``) are also left verbatim.

The empty string is a valid input and returns the empty string. Non-string
arguments raise ``TypeError``.
