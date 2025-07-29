"""Tests for validators.py – validation and resolution logic for config values."""

import argparse
import pytest
import re
from pathlib import Path

from charfinder.config import constants as C
from charfinder.config import messages as M
from charfinder import validators as V
from charfinder.fuzzymatchlib import FUZZY_ALGORITHM_REGISTRY
from charfinder.config.types import FuzzyConfig

# ---------------------------------------------------------------------
# Fuzzy Algorithm Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("algo", C.VALID_FUZZY_ALGO_NAMES)
def test_validate_fuzzy_algo_accepts_valid(algo: str) -> None:
    """Should return valid fuzzy algorithms unchanged."""
    assert V.validate_fuzzy_algo(algo) == algo


def test_validate_fuzzy_algo_rejects_invalid() -> None:
    """Should raise ValueError for unsupported algorithms."""
    invalid_algo = "notarealalgo"
    valid_options = sorted(set(C.FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    expected_msg = M.MSG_ERROR_UNSUPPORTED_ALGO_INPUT.format(
        name=invalid_algo,
        valid_options=", ".join(valid_options),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        V.validate_fuzzy_algo(invalid_algo)


# Validate FuzzyAlgoAction

def test_validate_fuzzy_algo_action_valid() -> None:
    """Should normalize and validate fuzzy algo via argparse action."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--fuzzy-algo", action=V.ValidateFuzzyAlgoAction)
    args = parser.parse_args(["--fuzzy-algo", "levenshtein"])
    assert args.fuzzy_algo == "levenshtein_ratio"


def test_validate_fuzzy_algo_action_none() -> None:
    """Should raise if value is None (missing from CLI)."""
    action = V.ValidateFuzzyAlgoAction(option_strings=["--fuzzy-algo"], dest="fuzzy_algo")
    parser = argparse.ArgumentParser()
    with pytest.raises(ValueError, match=re.escape(M.MSG_ERROR_MISSING_FUZZY_ALGO_VALUE)):
        action(parser, argparse.Namespace(), None)


def test_validate_fuzzy_algo_action_empty_list() -> None:
    """Should raise if passed an empty list of values."""
    action = V.ValidateFuzzyAlgoAction(option_strings=["--fuzzy-algo"], dest="fuzzy_algo")
    parser = argparse.ArgumentParser()
    with pytest.raises(ValueError, match=re.escape(M.MSG_ERROR_EMPTY_FUZZY_ALGO_LIST)):
        action(parser, argparse.Namespace(), [])

# apply_fuzzy_defaults

def test_apply_fuzzy_defaults_applies_when_missing() -> None:
    """Should apply fuzzy_algo and match_mode from config when missing."""
    args = argparse.Namespace(fuzzy=True)
    config = FuzzyConfig(fuzzy_algo="token_sort_ratio", fuzzy_match_mode="single")
    V.apply_fuzzy_defaults(args, config)
    assert args.fuzzy_algo == "token_sort_ratio"
    assert args.fuzzy_match_mode == "single"


def test_apply_fuzzy_defaults_does_not_override_existing() -> None:
    """Should not override values already set."""
    args = argparse.Namespace(
        fuzzy=True, fuzzy_algo="custom", fuzzy_match_mode="hybrid"
    )
    config = FuzzyConfig(fuzzy_algo="token_sort_ratio", fuzzy_match_mode="hybrid")
    V.apply_fuzzy_defaults(args, config)
    assert args.fuzzy_algo == "custom"
    assert args.fuzzy_match_mode == "hybrid"

# ---------------------------------------------------------------------
# Match Mode Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("mode", C.VALID_FUZZY_MATCH_MODES)
def test_validate_fuzzy_match_mode_valid(mode: str) -> None:
    """Should accept valid fuzzy match modes."""
    assert V.validate_fuzzy_match_mode(mode) == mode


def test_validate_fuzzy_match_mode_invalid() -> None:
    """Should raise for invalid match mode."""
    value = "invalid_mode"
    expected_msg = M.MSG_ERROR_INVALID_FUZZY_MATCH_MODE.format(
        value=value,
        valid_options=", ".join(sorted(C.VALID_FUZZY_MATCH_MODES)),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        V.validate_fuzzy_match_mode(value)


@pytest.mark.parametrize("mode", C.VALID_EXACT_MATCH_MODES)
def test_validate_exact_match_mode_valid(mode: str) -> None:
    """Should accept valid exact match modes."""
    assert V.validate_exact_match_mode(mode) == mode


def test_validate_exact_match_mode_invalid() -> None:
    """Should raise for invalid exact match mode."""
    value = "badmode"
    expected_msg = M.MSG_ERROR_INVALID_EXACT_MATCH_MODE.format(
        value=value,
        valid_options=", ".join(sorted(C.VALID_EXACT_MATCH_MODES)),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        V.validate_exact_match_mode(value)

# ---------------------------------------------------------------------
# Aggregation Function Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("agg", C.VALID_HYBRID_AGG_FUNCS)
def test_validate_hybrid_agg_fn_valid(agg: str) -> None:
    """Should accept all valid hybrid aggregation functions."""
    assert V.validate_hybrid_agg_fn(agg) == agg


def test_validate_hybrid_agg_fn_invalid() -> None:
    """Should raise for unknown hybrid aggregation functions."""
    func = "funkyavg"
    expected_msg = M.MSG_ERROR_INVALID_AGG_FUNC.format(
        func=func,
        valid_options=", ".join(sorted(C.VALID_HYBRID_AGG_FUNCS)),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        V.validate_hybrid_agg_fn(func)

# ---------------------------------------------------------------------
# Threshold Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("threshold", [0.0, 0.5, 1.0])
def test_validate_threshold_valid_values(threshold: float) -> None:
    """Should accept thresholds between 0.0 and 1.0 inclusive."""
    assert V.validate_threshold(threshold) == threshold


@pytest.mark.parametrize("threshold", [-0.1, 1.1, 99])
def test_validate_threshold_out_of_bounds(threshold: float) -> None:
    """Should raise ValueError for out-of-bound threshold values."""
    with pytest.raises(ValueError, match=re.escape(M.MSG_ERROR_INVALID_THRESHOLD)):
        V.validate_threshold(threshold)


def test_validate_threshold_type_error() -> None:
    """Should raise TypeError for non-numeric threshold values."""
    with pytest.raises(TypeError, match=re.escape(M.MSG_ERROR_INVALID_THRESHOLD_TYPE)):
        V.validate_threshold("0.5")  # type: ignore


# ---------------------------------------------------------------------
# Color Mode Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("color", C.VALID_COLOR_MODES)
def test_validate_color_mode_valid(color: str) -> None:
    """Should accept all valid color modes."""
    assert V.validate_color_mode(color) == color


def test_validate_color_mode_invalid() -> None:
    """Should raise for unknown color mode."""
    with pytest.raises(ValueError, match=re.escape("Invalid color mode")):
        V.validate_color_mode("blackandwhite")

# ---------------------------------------------------------------------
# Output Format Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("fmt", C.VALID_OUTPUT_FORMATS)
def test_validate_output_format_valid(fmt: str) -> None:
    """Should accept all valid output formats."""
    assert V.validate_output_format(fmt) == fmt

def test_validate_output_format_invalid() -> None:
    """Should raise for unsupported output format."""
    valid_options = ", ".join(sorted(C.VALID_OUTPUT_FORMATS))
    expected_msg = M.MSG_ERROR_INVALID_OUTPUT_FORMAT.format(format="xml", valid_options=valid_options)
    with pytest.raises(ValueError, match=expected_msg):
        V.validate_output_format("xml")

# ---------------------------------------------------------------------
# Show Score Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("val", ["true", "1", "yes"])
def test_validate_show_score_truthy(val: str) -> None:
    """Should resolve truthy values to True."""
    assert V.validate_show_score(val) is True


@pytest.mark.parametrize("val", ["false", "0", "no"])
def test_validate_show_score_falsy(val: str) -> None:
    """Should resolve falsy values to False."""
    assert V.validate_show_score(val) is False



def test_validate_show_score_invalid() -> None:
    """Should raise for unknown show score values."""
    valid_options = ", ".join(sorted(C.VALID_SHOW_SCORES))
    expected_msg = M.MSG_ERROR_INVALID_SHOW_SCORE_VALUE.format(value="maybe", valid_options=valid_options)
    with pytest.raises(argparse.ArgumentTypeError, match=expected_msg):
        V.validate_show_score("maybe")
        
# ---------------------------------------------------------------------
# Effective Resolver Logic
# ---------------------------------------------------------------------

# Threshold Validators

def test_resolve_effective_threshold_invalid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid env var should trigger fallback to default."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "not-a-float")
    assert V.resolve_effective_threshold(None) == C.DEFAULT_THRESHOLD


def test_resolve_effective_threshold_cli_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI value should override environment variable."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "0.1")
    assert V.resolve_effective_threshold(0.9) == 0.9


def test_resolve_effective_threshold_env_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment value should be used if CLI is None."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "0.75")
    assert V.resolve_effective_threshold(None) == 0.75


def test_resolve_effective_threshold_out_of_range(monkeypatch: pytest.MonkeyPatch) -> None:
    """Out-of-range env var should fallback to default with warning."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "2.0")
    assert V.resolve_effective_threshold(None) == C.DEFAULT_THRESHOLD


def test_resolve_effective_threshold_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default should be used if CLI and ENV are missing."""
    monkeypatch.delenv("CHARFINDER_MATCH_THRESHOLD", raising=False)
    assert V.resolve_effective_threshold(None) == C.DEFAULT_THRESHOLD


# Color Mode Validators

def test_resolve_effective_color_mode_cli_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI value should override environment variable."""
    monkeypatch.setenv("CHARFINDER_COLOR_MODE", "always")
    assert V.resolve_effective_color_mode("never") == "never"


def test_resolve_effective_color_mode_env_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment value should be used if CLI is None."""
    monkeypatch.setenv("CHARFINDER_COLOR_MODE", "auto")
    assert V.resolve_effective_color_mode(None) == "auto"


def test_resolve_effective_color_mode_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default should be used if CLI and ENV are missing."""
    monkeypatch.delenv("CHARFINDER_COLOR_MODE", raising=False)
    assert V.resolve_effective_color_mode(None) == C.DEFAULT_COLOR_MODE


def test_resolve_effective_color_mode_env_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Should fall back to default if ENV value is invalid."""
    monkeypatch.setenv("CHARFINDER_COLOR_MODE", "invalid_mode")
    assert V.resolve_effective_color_mode(None) == C.DEFAULT_COLOR_MODE


def test_resolve_effective_color_mode_cli_invalid_fallbacks_to_default() -> None:
    """Invalid CLI color mode should fall back to default without raising."""
    result = V.resolve_effective_color_mode("blackandwhite")
    assert result == C.DEFAULT_COLOR_MODE



# Show Score Validators

def test_resolve_effective_show_score_cli_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI value should override environment variable."""
    monkeypatch.setenv("CHARFINDER_SHOW_SCORE", "no")
    assert V.resolve_effective_show_score(cli_value=True) is True


def test_resolve_effective_show_score_env_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment value should be used if CLI is None."""
    monkeypatch.setenv("CHARFINDER_SHOW_SCORE", "yes")
    assert V.resolve_effective_show_score(cli_value=None) is True


def test_resolve_effective_show_score_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default should be used if CLI and ENV are missing."""
    monkeypatch.delenv("CHARFINDER_SHOW_SCORE", raising=False)
    assert V.resolve_effective_show_score(cli_value=None) == C.DEFAULT_SHOW_SCORE


# ---------------------------------------------------------------------
# Cache File
# ---------------------------------------------------------------------

def test_validate_cache_file_path_accepts_path() -> None:
    """Should accept and return Path input."""
    path = Path("some/path/cache.json")
    assert V.validate_cache_file_path(path) == path


def test_validate_cache_file_path_accepts_str() -> None:
    """Should convert string path to Path."""
    result = V.validate_cache_file_path(Path("some/path/cache.json"))
    assert isinstance(result, Path)
    assert result.name == "cache.json"


def test_validate_cache_file_path_returns_default_when_none() -> None:
    """Should return default path if input is None."""
    result = V.validate_cache_file_path(None)
    assert isinstance(result, Path)
    assert "cache" in str(result)


def test_validate_cache_file_path_type_error() -> None:
    """Should raise if given non-str/Path."""
    with pytest.raises(TypeError, match=M.MSG_ERROR_INVALID_PATH_TYPE.format(type=int)):
        V.validate_cache_file_path(123)  # type: ignore

@pytest.mark.parametrize("val", [True, False])
def test_validate_cache_rebuild_flag_valid(val: bool) -> None:
    assert V.validate_cache_rebuild_flag(force_rebuild=val) is val


def test_validate_cache_rebuild_flag_type_error() -> None:
    with pytest.raises(TypeError, match="Expected a boolean value."):
        V.validate_cache_rebuild_flag(force_rebuild="yes")  # type: ignore


def test_validate_dict_str_keys_valid() -> None:
    input_dict = {"a": {"name": "ok"}}
    assert V.validate_dict_str_keys(input_dict) == input_dict


def test_validate_dict_str_keys_invalid_key() -> None:
    with pytest.raises(TypeError):
        V.validate_dict_str_keys({1: {}})  # type: ignore


def test_validate_dict_str_keys_invalid_value() -> None:
    with pytest.raises(TypeError):
        V.validate_dict_str_keys({"a": 123})  # type: ignore


def test_validate_name_cache_structure_valid() -> None:
    V.validate_name_cache_structure({
        "x": {"original": "A", "normalized": "a"},
        "y": {"original": "B", "normalized": "b"},
    })


def test_validate_name_cache_structure_missing_keys() -> None:
    with pytest.raises(ValueError, match="Missing required keys"):
        V.validate_name_cache_structure({"x": {"original": "X"}})


def test_validate_name_cache_structure_invalid_entry_type() -> None:
    with pytest.raises(TypeError):
        V.validate_name_cache_structure({"x": "notadict"})

# ---------------------------------------------------------------------
# Unicode Data
# ---------------------------------------------------------------------

def test_validate_unicode_data_url_valid() -> None:
    assert V.validate_unicode_data_url("https://example.com/file.txt") is True


@pytest.mark.parametrize("url", ["ftp://site.com", "noscheme.com", "http:///bad"])
def test_validate_unicode_data_url_invalid(url: str) -> None:
    with pytest.raises(ValueError):
        V.validate_unicode_data_url(url)


def test_validate_files_and_url_returns_error(tmp_path: Path) -> None:
    """Should return message string when validation fails."""
    bad_url = "ftp://example.com"
    bad_file = tmp_path / "nonexistent.txt"
    msg = V.validate_files_and_url(bad_url, bad_file)
    assert isinstance(msg, str)
    assert "Validation failed" in msg


def test_validate_files_and_url_success(tmp_path: Path) -> None:
    """Should return None when validation passes."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")
    msg = V.validate_files_and_url("https://example.com", file_path)
    assert msg is None


# ---------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------

def test_validate_normalized_name_valid() -> None:
    assert V.validate_normalized_name("ABC") == "ABC"


@pytest.mark.parametrize("val", [None, "", "   "])
def test_validate_normalized_name_invalid(val: str | None) -> None:
    with pytest.raises(ValueError, match=M.MSG_ERROR_INVALID_NAME.format(value=val)):
        V.validate_normalized_name(val)  # type: ignore
