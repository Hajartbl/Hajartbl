"""
Pipeline orchestrator — wires extract -> validate -> transform -> load together
and returns a run report (counts + timing) for observability.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .extract import read_sources
from .validate import load_schema, validate
from .transform import aggregate_kpis, deduplicate, enrich
from .load import load


@dataclass
class RunReport:
    rows_read: int = 0
    rows_valid: int = 0
    rows_rejected: int = 0
    rows_after_dedup: int = 0
    kpi_rows: int = 0
    seconds: float = 0.0
    db_stats: dict = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"read={self.rows_read} valid={self.rows_valid} "
            f"rejected={self.rows_rejected} deduped={self.rows_after_dedup} "
            f"kpis={self.kpi_rows} in {self.seconds * 1000:.1f} ms"
        )


def run_pipeline(sources: list[str], schema_path: str, db_path: str,
                 rejects_path: str | None = None) -> RunReport:
    """Run the full ETL and return a RunReport."""
    start = time.perf_counter()
    schema = load_schema(schema_path)

    raw = read_sources(sources)
    valid, rejected = validate(raw, schema)

    if rejects_path is not None and not rejected.empty:
        rejected.to_csv(rejects_path, index=False)

    deduped = deduplicate(valid, schema["primary_key"])
    enriched = enrich(deduped)
    kpis = aggregate_kpis(enriched)
    db_stats = load(enriched, kpis, db_path)

    return RunReport(
        rows_read=len(raw),
        rows_valid=len(valid),
        rows_rejected=len(rejected),
        rows_after_dedup=len(deduped),
        kpi_rows=len(kpis),
        seconds=time.perf_counter() - start,
        db_stats=db_stats,
    )
