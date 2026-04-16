"""Tests for argus.export.selector — category-diverse top-3 selection."""

from __future__ import annotations

from argus.export.selector import select_top_3


def _entry(score: int, category: str, fid: str) -> dict:
    return {
        "finding": {"id": fid, "category": category},
        "score": score,
    }


def test_returns_all_when_fewer_than_three():
    entries = [_entry(10, "a", "X1"), _entry(8, "b", "X2")]
    assert select_top_3(entries) == entries


def test_prefers_category_diversity():
    # Highest-scored same-category finding should lose to a diverse mix.
    entries = [
        _entry(14, "web_application", "A"),
        _entry(13, "web_application", "B"),
        _entry(12, "web_application", "C"),
        _entry(11, "infrastructure",  "D"),
        _entry(10, "email_security",  "E"),
    ]
    top = select_top_3(entries)
    ids = [e["finding"]["id"] for e in top]
    categories = [e["finding"]["category"] for e in top]
    assert ids == ["A", "D", "E"]
    assert len(set(categories)) == 3


def test_falls_back_to_score_when_no_diversity():
    # All same category: pick top 3 by score.
    entries = [
        _entry(14, "web_application", "A"),
        _entry(13, "web_application", "B"),
        _entry(12, "web_application", "C"),
        _entry(11, "web_application", "D"),
    ]
    top = select_top_3(entries)
    assert [e["finding"]["id"] for e in top] == ["A", "B", "C"]


def test_mixed_fills_with_remaining_by_score():
    # Only two distinct categories — third slot fills with next-best regardless.
    entries = [
        _entry(14, "web_application", "A"),
        _entry(13, "infrastructure",  "B"),
        _entry(12, "web_application", "C"),
        _entry(11, "web_application", "D"),
    ]
    top = select_top_3(entries)
    ids = [e["finding"]["id"] for e in top]
    assert ids[:2] == ["A", "B"]
    assert ids[2] == "C"  # next-highest by score


def test_exactly_three_returns_all_three():
    entries = [
        _entry(10, "x", "A"),
        _entry(9,  "y", "B"),
        _entry(8,  "z", "C"),
    ]
    assert len(select_top_3(entries)) == 3
