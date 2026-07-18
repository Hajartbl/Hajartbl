"""
Extraction layer — read heterogeneous source formats into a single DataFrame.

Supported formats: CSV, Excel (.xlsx), JSON, XML. The format is inferred from
the file extension, so callers just point the pipeline at a file and go.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET

import pandas as pd

_CSV = {".csv", ".tsv"}
_EXCEL = {".xlsx", ".xls"}
_JSON = {".json"}
_XML = {".xml"}


def read_source(path: str) -> pd.DataFrame:
    """Read a single source file into a DataFrame, dispatching on extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext in _CSV:
        sep = "\t" if ext == ".tsv" else ","
        return pd.read_csv(path, sep=sep)
    if ext in _EXCEL:
        return pd.read_excel(path)
    if ext in _JSON:
        return pd.read_json(path)
    if ext in _XML:
        return _read_xml(path)
    raise ValueError(f"Unsupported source format: {ext!r} ({path})")


def _read_xml(path: str) -> pd.DataFrame:
    """Flatten a simple <records><record><field>..</field></record></records> tree."""
    root = ET.parse(path).getroot()
    rows = []
    for record in root:
        rows.append({child.tag: child.text for child in record})
    return pd.DataFrame(rows)


def read_sources(paths: list[str]) -> pd.DataFrame:
    """Read and vertically concatenate several source files of any supported type."""
    frames = [read_source(p) for p in paths]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
