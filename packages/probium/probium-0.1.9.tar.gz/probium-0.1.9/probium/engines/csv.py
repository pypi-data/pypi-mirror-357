from __future__ import annotations

from ..scoring import score_magic, score_tokens
from ..models import Candidate, Result
from .base import EngineBase
from ..registry import register
import csv, io

@register
class CSVEngine(EngineBase):
    name = "csv"
    cost = 0.05

    DELIMS = ",;\t|"

    MIN_ROWS = 3

    def sniff(self, payload: bytes) -> Result:
        try:
            text = payload.decode("utf-8", errors="replace")

            if "�" in text or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                return Result(candidates=[])


            lines = text.splitlines()
            if len(lines) < self.MIN_ROWS:
                return Result(candidates=[])

            sample_text = "\n".join(lines[:10])
            dialect = csv.Sniffer().sniff(sample_text, self.DELIMS)

            delim_count = sum(dialect.delimiter in ln for ln in lines[:10])
            if delim_count < self.MIN_ROWS:
                return Result(candidates=[])

            reader = csv.reader(io.StringIO(sample_text), dialect)
            rows = [row for row in reader if row]
            if len(rows) < self.MIN_ROWS:
                return Result(candidates=[])


            row_lengths = {len(r) for r in rows}
            if len(row_lengths) == 1 and list(row_lengths)[0] > 1:
                has_header = csv.Sniffer().has_header(sample_text)
                ratio = 1.0 if has_header else 0.5
                cand = Candidate(
                    media_type="text/csv",
                    extension="csv",
                    confidence=score_tokens(ratio),
                    breakdown={"token_ratio": ratio},
                )
                return Result(candidates=[cand])
        except Exception:
            pass
        return Result(candidates=[])
