"""Decode HTML character entities to their Unicode characters.

Supports:
  - Named entities: ``&amp;`` -> ``&``, ``&copy;`` -> ``©``
  - Decimal numeric entities: ``&#38;`` -> ``&``, ``&#169;`` -> ``©``
  - Hex numeric entities:     ``&#x26;`` -> ``&``, ``&#xa9;`` -> ``©``

A single-pass regex substitution is used instead of chained ``.replace``
calls so entities produced by decoding are NOT re-processed. That would
be a real bug: ``&amp;#38;`` would become ``&#38;`` and then ``&``, which
is not what browsers do. We decode exactly once.
"""

from __future__ import annotations

import re
import html.entities
import unicodedata

__all__ = ["decode_entities", "decode_entities_in_string"]

_ENTITY_RE = re.compile(r"&(#[0-9]+|#[xX][0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]*);")


def _replacement(m: re.Match) -> str:
    body = m.group(1)

    if body.startswith("#x") or body.startswith("#X"):
        try:
            code = int(body[2:], 16)
        except ValueError:
            return m.group(0)
    elif body.startswith("#"):
        try:
            code = int(body[1:], 10)
        except ValueError:
            return m.group(0)
    else:
        name = body
        try:
            return html.entities.html5[name]
        except KeyError:
            return m.group(0)

    if not (0 <= code <= 0x10FFFF):
        return m.group(0)

    try:
        return chr(code)
    except (ValueError, OverflowError):
        return m.group(0)


def decode_entities(text: str) -> str:
    """Replace HTML character entities in *text* with their characters.

    Unknown entities (bad names, invalid code points, malformed numbers) are
    left verbatim in the output. Entities are decoded exactly once, so an
    entity that appears as the result of decoding another entity is left
    alone — mirroring what browsers do for plain-text contexts.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str, got " + type(text).__name__)
    return _ENTITY_RE.sub(_replacement, text)


# A friendlier name for callers reading prose like "decode entities in a string".
decode_entities_in_string = decode_entities
