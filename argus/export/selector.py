"""Stage 4 — pick the top 3 findings for the email body.

Without category diversity the same finding type would populate all three
slots (e.g. phpMyAdmin × 3 on different paths). The prospect reads
"database database database" instead of three independent 'oh shit'
moments. Category diversity is one of the strongest conversion levers
in the pipeline.
"""

from __future__ import annotations


def select_top_3(scored_findings: list[dict]) -> list[dict]:
    """Return up to 3 entries, preferring category diversity.

    Pass 1: highest finding from each unique category until slots fill.
    Pass 2: fill remaining slots with next-highest regardless of category.
    Scored list is assumed pre-sorted by score descending.
    """
    if len(scored_findings) <= 3:
        return list(scored_findings)

    selected: list[dict] = []
    selected_ids: set[int] = set()
    used_categories: set[str] = set()

    for entry in scored_findings:
        if len(selected) >= 3:
            break
        cat = entry["finding"].get("category", "") or ""
        if cat not in used_categories:
            selected.append(entry)
            selected_ids.add(id(entry))
            used_categories.add(cat)

    if len(selected) < 3:
        for entry in scored_findings:
            if id(entry) in selected_ids:
                continue
            selected.append(entry)
            selected_ids.add(id(entry))
            if len(selected) >= 3:
                break

    return selected[:3]
