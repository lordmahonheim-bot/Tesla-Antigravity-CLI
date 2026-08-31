#!/usr/bin/env python3
"""Strict minimal YAML-subset parser (stdlib-only, deterministic, fail-closed).

Vigilum Codex 2.1 hardening principle (P3 / P7): an unparsable document is
NEVER coerced into a permissive structure. This parser supports exactly the
canonical subset used by Tesla Mission Graphs and governance artifacts:

- Block mappings (``key: value``) and block sequences (``- item``)
- Nested indentation
- Inline flow collections ``[a, b]`` and ``{k: v}``
- Scalars: null / bool / int / float / quoted string / plain string
- ``#`` comments (full-line and trailing, outside quotes)

Anything else (anchors, tags, block scalars ``|``/``>``, multi-document,
tabs as indentation, duplicate keys) raises :class:`YamlMiniError`.
The caller decides whether to map that to BLOCKED or UNKNOWN (never PASS).

Dependency-free by design: identical behavior with or without PyYAML.
"""
from __future__ import annotations

import json
import re
from typing import Any


class YamlMiniError(ValueError):
    """Raised when the document is outside the supported strict subset."""


_INT_RE = re.compile(r"^[-+]?\d+$")
_FLOAT_RE = re.compile(r"^[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?$")


def _strip_comment(line: str) -> str:
    """Remove a trailing ``# comment`` when not inside a quoted region."""
    quote: str | None = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote is not None:
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            i += 1
            continue
        if ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[:i].rstrip()
        i += 1
    return line.rstrip()


def _preprocess(text: str) -> list[tuple[int, str]]:
    """Return [(indent, content), ...] for meaningful lines; reject tabs."""
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if "\t" in raw[:1] or "\t" in raw[: len(raw) - len(raw.lstrip(" "))]:
            raise YamlMiniError("tab character used for indentation")
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        content = stripped[indent:].rstrip()
        if not content:
            continue
        lines.append((indent, content))
    return lines


def _top_level_colon(text: str) -> bool:
    """True when ``text`` contains a ':' outside quotes (mapping indicator)."""
    quote: str | None = None
    for ch in text:
        if quote is not None:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch == ":":
            return True
    return False


def _split_top(text: str, sep: str) -> list[str]:
    """Split on ``sep`` outside quotes and flow brackets."""
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for ch in text:
        if quote is not None:
            current.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            current.append(ch)
        elif ch in "[{":
            depth += 1
            current.append(ch)
        elif ch in "]}":
            depth -= 1
            current.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if quote is not None:
        raise YamlMiniError("unterminated quoted string")
    parts.append("".join(current).strip())
    return parts


def _parse_scalar(text: str) -> Any:
    text = text.strip()
    if not text:
        return None
    if text[0] == '"' and text[-1] == '"':
        try:
            return json.loads(text)
        except ValueError as exc:
            raise YamlMiniError(f"invalid double-quoted scalar: {text!r}") from exc
    if text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    low = text.lower()
    if low in ("null", "~"):
        return None
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if _INT_RE.fullmatch(text):
        return int(text)
    if _FLOAT_RE.fullmatch(text):
        return float(text)
    if text[0] == "[" and text[-1] == "]":
        inner = text[1:-1].strip()
        return [] if not inner else [_parse_scalar(part) for part in _split_top(inner, ",")]
    if text[0] == "{" and text[-1] == "}":
        inner = text[1:-1].strip()
        out: dict[str, Any] = {}
        if inner:
            for part in _split_top(inner, ","):
                if not _top_level_colon(part):
                    raise YamlMiniError(f"flow mapping entry without ':' separator: {part!r}")
                key, _, value = part.partition(":")
                out[str(_parse_scalar(key))] = _parse_scalar(value)
        return out
    return text


def _block(lines: list[tuple[int, str]], idx: int, indent: int) -> tuple[Any, int]:
    """Parse the block starting at ``lines[idx]`` (which has column ``indent``)."""
    if idx >= len(lines) or lines[idx][0] != indent:
        raise YamlMiniError("internal block alignment error")
    text = lines[idx][1]

    if text.startswith("- "):
        items: list[Any] = []
        while idx < len(lines):
            ind, content = lines[idx]
            if ind != indent or not content.startswith("- "):
                break
            rest = content[2:].strip()
            if rest.startswith("- "):
                raise YamlMiniError("nested inline sequence on one line is unsupported")
            if not rest:
                idx += 1
                if idx < len(lines) and lines[idx][0] > indent + 2:
                    sub, idx = _block(lines, idx, lines[idx][0])
                    items.append(sub)
                else:
                    items.append(None)
                continue
            if _top_level_colon(rest):
                # Mapping item: "- key: value" (possibly followed by deeper lines)
                key, _, value = rest.partition(":")
                key = key.strip()
                if not key:
                    raise YamlMiniError("empty mapping key in sequence item")
                item: dict[str, Any] = {}
                value = value.strip()
                idx += 1
                if value:
                    item[key] = _parse_scalar(value)
                elif idx < len(lines) and lines[idx][0] > indent + 2:
                    sub, idx = _block(lines, idx, lines[idx][0])
                    item[key] = sub
                else:
                    item[key] = None
                # Continuation mapping lines aligned at indent+2
                while idx < len(lines):
                    cind, ctext = lines[idx]
                    if cind != indent + 2 or ctext.startswith("- "):
                        break
                    if not _top_level_colon(ctext):
                        raise YamlMiniError(f"expected 'key: value', got: {ctext!r}")
                    ck, _, cv = ctext.partition(":")
                    ck = ck.strip()
                    cv = cv.strip()
                    idx += 1
                    if cv:
                        item[ck] = _parse_scalar(cv)
                    elif idx < len(lines) and lines[idx][0] > indent + 4:
                        sub, idx = _block(lines, idx, lines[idx][0])
                        item[ck] = sub
                    else:
                        item[ck] = None
                items.append(item)
            else:
                items.append(_parse_scalar(rest))
                idx += 1
        return items, idx

    # Block mapping
    out: dict[str, Any] = {}
    while idx < len(lines):
        ind, content = lines[idx]
        if ind != indent or content.startswith("- "):
            break
        if not _top_level_colon(content):
            raise YamlMiniError(f"expected 'key: value', got: {content!r}")
        key, _, value = content.partition(":")
        key = key.strip()
        if not key:
            raise YamlMiniError("empty mapping key")
        if key in out:
            raise YamlMiniError(f"duplicate mapping key: {key!r}")
        value = value.strip()
        idx += 1
        if value:
            out[key] = _parse_scalar(value)
        elif idx < len(lines) and lines[idx][0] > indent:
            sub, idx = _block(lines, idx, lines[idx][0])
            out[key] = sub
        else:
            out[key] = None
    return out, idx


def parse(text: str) -> Any:
    """Parse the YAML subset document; raise :class:`YamlMiniError` on any deviation."""
    lines = _preprocess(text)
    if not lines:
        return None
    value, idx = _block(lines, 0, lines[0][0])
    if idx != len(lines):
        raise YamlMiniError(f"unexpected trailing content at line {idx + 1}")
    return value


def load_file(path: str | Any) -> Any:
    """Parse a YAML file, wrapping read errors as :class:`YamlMiniError`."""
    from pathlib import Path
    try:
        return parse(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise YamlMiniError(f"cannot read YAML file {path}: {exc}") from exc
