"""Tests for argus.export.tier — tier classification and upgrade logic."""

from __future__ import annotations

from argus.export.tier import classify_tier, maybe_upgrade


def _s(score: int) -> dict:
    return {"finding": {"id": f"X-{score}"}, "score": score}


def test_empty_is_skip():
    assert classify_tier([]) == "SKIP"


def test_threshold_a_inclusive():
    assert classify_tier([_s(18)]) == "A"
    assert classify_tier([_s(19)]) == "A"
    assert classify_tier([_s(50)]) == "A"


def test_threshold_b_range():
    assert classify_tier([_s(17)]) == "B"
    assert classify_tier([_s(10)]) == "B"


def test_threshold_c_range():
    assert classify_tier([_s(9)]) == "C"
    assert classify_tier([_s(5)]) == "C"


def test_below_c_is_skip():
    assert classify_tier([_s(4)]) == "SKIP"
    assert classify_tier([_s(0)]) == "SKIP"


def test_maybe_upgrade_b_to_a_with_three_above_ten():
    scored = [_s(14), _s(12), _s(11), _s(3)]
    assert classify_tier(scored) == "B"
    assert maybe_upgrade("B", scored) == "A"


def test_maybe_upgrade_does_not_upgrade_with_only_two_above_ten():
    scored = [_s(14), _s(11), _s(9), _s(8)]
    assert maybe_upgrade("B", scored) == "B"


def test_maybe_upgrade_ignores_a_and_c():
    scored = [_s(20), _s(15), _s(11)]
    assert maybe_upgrade("A", scored) == "A"
    scored_c = [_s(7), _s(6), _s(5)]
    assert maybe_upgrade("C", scored_c) == "C"


def test_maybe_upgrade_exactly_three_at_ten():
    scored = [_s(17), _s(10), _s(10), _s(10)]
    assert maybe_upgrade("B", scored) == "A"
