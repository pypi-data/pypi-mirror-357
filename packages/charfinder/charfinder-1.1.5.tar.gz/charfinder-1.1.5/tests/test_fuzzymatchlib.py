"""Tests for fuzzymatchlib.py all algorithms, modes, and combinations."""

import re
import pytest

from charfinder.fuzzymatchlib import (
    compute_similarity,
    get_fuzzy_algorithm_registry,
    resolve_algorithm_name,
    simple_ratio,
    normalized_ratio,
    levenshtein_ratio,
    token_sort_ratio_score,
    hybrid_score,
    FUZZY_ALGORITHM_REGISTRY,
)
from charfinder.validators import validate_hybrid_agg_fn
from charfinder.config.constants import (
    VALID_FUZZY_MATCH_MODES,
    VALID_HYBRID_AGG_FUNCS,
    FUZZY_ALGO_ALIASES,
)
from charfinder.config.aliases import (
    FuzzyAlgorithm,
    FuzzyMatchMode,
    HybridAggFunc,
)
from charfinder.config.messages import (
    MSG_ERROR_UNSUPPORTED_ALGO_INPUT,
    MSG_ERROR_INVALID_FUZZY_MATCH_MODE,
    MSG_ERROR_ALGO_NOT_FOUND,
    MSG_ERROR_AGG_FN_UNEXPECTED,
)

# ---------------------------------------------------------------------
# Parametrized Combinations
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "algorithm,mode,agg_fn",
    [
        *[(algo, "single", None) for algo in FUZZY_ALGORITHM_REGISTRY],
        *[(algo, "hybrid", agg_fn) for algo in FUZZY_ALGORITHM_REGISTRY
          if algo == "hybrid_score"
          for agg_fn in VALID_HYBRID_AGG_FUNCS],
    ],
)
def test_compute_similarity_combinations(
    algorithm: FuzzyAlgorithm,
    mode: FuzzyMatchMode,
    agg_fn: HybridAggFunc | None,
) -> None:
    """Test all algorithm * mode * agg_fn combinations."""
    score = compute_similarity("abc", "abc", algorithm=algorithm, mode=mode, agg_fn=agg_fn or "mean")
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

# ---------------------------------------------------------------------
# Individual Algorithm Tests
# ---------------------------------------------------------------------

def test_simple_ratio_exact_and_partial() -> None:
    assert simple_ratio("abc", "abc") == 1.0
    assert simple_ratio("abc", "axc") == 2 / 3
    assert simple_ratio("", "") == 0.0


def test_normalized_ratio_with_case_and_accents() -> None:
    assert normalized_ratio("CAFÉ", "CAFE") < 1.0
    assert normalized_ratio("café", "café") == 1.0
    assert normalized_ratio("CAFÉ", "CAFÉ") == 1.0
    assert normalized_ratio("Café", "café") == 1.0


def test_levenshtein_ratio_basic() -> None:
    assert levenshtein_ratio("kitten", "sitting") < 1.0
    assert levenshtein_ratio("abc", "abc") == 1.0


def test_token_sort_ratio_score_disorder() -> None:
    assert token_sort_ratio_score("a b c", "c b a") == 1.0
    assert 0.0 <= token_sort_ratio_score("abc", "xyz") <= 1.0


@pytest.mark.parametrize("agg_fn", sorted(VALID_HYBRID_AGG_FUNCS))
def test_hybrid_score_agg_functions(agg_fn: HybridAggFunc) -> None:
    score = hybrid_score("hello", "hxlxo", agg_fn=agg_fn)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_token_subset_ratio_score_behavior() -> None:
    """Test token_subset_ratio_score on common, no-match, and partial-match cases."""
    from charfinder.fuzzymatchlib import token_subset_ratio_score

    # Full token match (should yield 1.0)
    assert token_subset_ratio_score("face kiss", "kiss face") == pytest.approx(1.0)

    # Partial token match (1 of 2 match, so coverage = 0.5, sort ratio = 100%)
    assert token_subset_ratio_score("face kiss", "kiss dummy") == pytest.approx(0.5)

    # No token overlap (should be 0.0)
    assert token_subset_ratio_score("abc", "xyz") == 0.0

    # Identical multiword sentence
    assert token_subset_ratio_score("a b c", "a b c") == 1.0

    # Subset match with order preserved
    assert token_subset_ratio_score("this is a test", "this test") < 1.0

    # Empty input strings
    assert token_subset_ratio_score("", "") == 0.0
    assert token_subset_ratio_score("nonempty", "") == 0.0
    assert token_subset_ratio_score("", "nonempty") == 0.0

# ---------------------------------------------------------------------
# Resolver Tests
# ---------------------------------------------------------------------

@pytest.mark.parametrize("alias,expected", sorted(FUZZY_ALGO_ALIASES.items()))
def test_resolve_algorithm_name_aliases(alias: str, expected: FuzzyAlgorithm) -> None:
    resolved = resolve_algorithm_name(alias)
    assert resolved == expected


def test_resolve_algorithm_name_known_registry_name() -> None:
    for algo in FUZZY_ALGORITHM_REGISTRY:
        resolved = resolve_algorithm_name(algo)
        assert resolved == algo


def test_resolve_algorithm_name_invalid() -> None:
    """It should raise ValueError for unsupported algorithm name."""
    invalid_name = "foo"
    valid_options = sorted(set(FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    expected_msg = MSG_ERROR_UNSUPPORTED_ALGO_INPUT.format(
        name=invalid_name,
        valid_options=", ".join(valid_options),
    )
    print(f"[TEST expected message: {expected_msg}] ")
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        resolve_algorithm_name(invalid_name)
# ---------------------------------------------------------------------
# Registry Access
# ---------------------------------------------------------------------

def test_get_fuzzy_algorithm_registry_contains_expected() -> None:
    registry = get_fuzzy_algorithm_registry()
    assert isinstance(registry, list)
    assert "levenshtein_ratio" in registry
    assert set(registry) == set(FUZZY_ALGORITHM_REGISTRY.keys())

    

# ---------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------

def test_compute_similarity_with_invalid_mode() -> None:
    """It should raise ValueError for invalid fuzzy match mode."""
    invalid_mode = "invalid"
    expected_msg = MSG_ERROR_INVALID_FUZZY_MATCH_MODE.format(
        value=invalid_mode,
        valid_options=", ".join(sorted(VALID_FUZZY_MATCH_MODES)),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        compute_similarity("a", "b", algorithm="simple_ratio", mode=invalid_mode)  # type: ignore


def test_compute_similarity_with_unregistered_algorithm() -> None:
    """It should raise ValueError if the algorithm is not in the registry."""
    algorithm = "unknown"
    valid_options = sorted(set(FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    expected_msg = MSG_ERROR_UNSUPPORTED_ALGO_INPUT.format(
        name=algorithm,
        valid_options=", ".join(valid_options),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        compute_similarity("a", "b", algorithm=algorithm)  # type: ignore

from charfinder.config.messages import MSG_ERROR_INVALID_AGG_FUNC

def test_hybrid_score_rejects_invalid_agg_fn() -> None:
    """Should raise ValueError for unsupported aggregation function."""
    expected_msg = MSG_ERROR_INVALID_AGG_FUNC.format(
        func="unsupported", valid_options=", ".join(sorted(VALID_HYBRID_AGG_FUNCS))
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        hybrid_score("abc", "def", agg_fn="unsupported")  # type: ignore[arg-type]


def test_hybrid_score_runtime_error_on_unreachable_agg_fn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Covers unreachable RuntimeError fallback in hybrid_score()."""

    class FakeAgg(str):
        def __eq__(self, other: object) -> bool:
            return False

    fake_value = FakeAgg("mean")
    expected_msg = MSG_ERROR_AGG_FN_UNEXPECTED.format(agg_fn="mean")
    # Patch the *local* validate_hybrid_agg_fn inside fuzzymatchlib to return fake_value
    monkeypatch.setattr("charfinder.fuzzymatchlib.validate_hybrid_agg_fn", lambda _: fake_value)

    with pytest.raises(RuntimeError, match=re.escape(expected_msg)):
        hybrid_score("abc", "xyz", agg_fn="mean")  # validator returns FakeAgg("mean")



def test_compute_similarity_registry_miss(monkeypatch: pytest.MonkeyPatch) -> None:
    """Should raise ValueError if algorithm is removed from registry before validation."""
    monkeypatch.delitem(FUZZY_ALGORITHM_REGISTRY, "simple_ratio", raising=False)

    from charfinder.config.messages import MSG_ERROR_UNSUPPORTED_ALGO_INPUT
    valid_options = sorted(set(FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    expected_msg = MSG_ERROR_UNSUPPORTED_ALGO_INPUT.format(
        name="simple_ratio", valid_options=", ".join(valid_options)
    )

    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        compute_similarity("abc", "abc", algorithm="simple_ratio")

# ---------------------------------------------------------------------
# Public API Coverage
# ---------------------------------------------------------------------

def test_compute_similarity_final_return() -> None:
    """Covers compute_similarity() returning resolved algorithm function call."""
    score = compute_similarity("abc", "xyz", algorithm="simple_ratio", mode="single")
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
