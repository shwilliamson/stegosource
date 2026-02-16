"""Tests for the Alpha Vantage API client tool."""

from __future__ import annotations

import json
import os
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from tools.alpha_vantage import (
    CACHE_TTL,
    VALID_INTERVALS,
    AlphaVantageError,
    ApiError,
    InvalidTickerError,
    MissingApiKeyError,
    RateLimitError,
    _cache,
    _cache_key,
    _get_api_key,
    _parse_time_series,
    clear_cache,
    fetch_daily,
    fetch_intraday,
    get_cached,
    set_cached,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Ensure each test starts with a clean cache."""
    clear_cache()


@pytest.fixture()
def api_key_env() -> dict[str, str]:
    """Return an environment dict with a test API key."""
    return {"ALPHAVANTAGE_API_KEY": "test-api-key-123"}


def _make_daily_response(
    symbol: str = "AAPL",
    num_days: int = 3,
) -> dict[str, Any]:
    """Create a mock Alpha Vantage daily time series response."""
    time_series: dict[str, dict[str, str]] = {}
    for i in range(num_days):
        date = f"2025-01-{15 - i:02d}"
        time_series[date] = {
            "1. open": f"{150.0 + i:.4f}",
            "2. high": f"{155.0 + i:.4f}",
            "3. low": f"{148.0 + i:.4f}",
            "4. close": f"{152.0 + i:.4f}",
            "5. volume": str(1000000 + i * 100000),
        }
    return {
        "Meta Data": {
            "1. Information": "Daily Prices",
            "2. Symbol": symbol,
        },
        "Time Series (Daily)": time_series,
    }


def _make_intraday_response(
    symbol: str = "AAPL",
    interval: str = "5min",
    num_points: int = 3,
) -> dict[str, Any]:
    """Create a mock Alpha Vantage intraday time series response."""
    time_series: dict[str, dict[str, str]] = {}
    for i in range(num_points):
        timestamp = f"2025-01-15 10:{i * 5:02d}:00"
        time_series[timestamp] = {
            "1. open": f"{150.0 + i:.4f}",
            "2. high": f"{155.0 + i:.4f}",
            "3. low": f"{148.0 + i:.4f}",
            "4. close": f"{152.0 + i:.4f}",
            "5. volume": str(50000 + i * 10000),
        }
    return {
        "Meta Data": {
            "1. Information": f"Intraday ({interval})",
            "2. Symbol": symbol,
        },
        f"Time Series ({interval})": time_series,
    }


# ---------------------------------------------------------------------------
# API key validation tests
# ---------------------------------------------------------------------------


class TestGetApiKey:
    """Verify API key retrieval and validation."""

    def test_returns_key_when_set(self) -> None:
        with patch.dict(os.environ, {"ALPHAVANTAGE_API_KEY": "my-key"}):
            assert _get_api_key() == "my-key"

    def test_raises_when_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ALPHAVANTAGE_API_KEY", None)
            with pytest.raises(MissingApiKeyError, match="ALPHAVANTAGE_API_KEY"):
                _get_api_key()

    def test_raises_when_empty(self) -> None:
        with patch.dict(os.environ, {"ALPHAVANTAGE_API_KEY": ""}):
            with pytest.raises(MissingApiKeyError):
                _get_api_key()

    def test_raises_when_whitespace(self) -> None:
        with patch.dict(os.environ, {"ALPHAVANTAGE_API_KEY": "   "}):
            with pytest.raises(MissingApiKeyError):
                _get_api_key()

    def test_strips_whitespace(self) -> None:
        with patch.dict(os.environ, {"ALPHAVANTAGE_API_KEY": "  my-key  "}):
            assert _get_api_key() == "my-key"


# ---------------------------------------------------------------------------
# Cache tests
# ---------------------------------------------------------------------------


class TestCache:
    """Verify session-level caching behavior."""

    def test_cache_key_daily(self) -> None:
        key = _cache_key("TIME_SERIES_DAILY", "aapl")
        assert key == "TIME_SERIES_DAILY:AAPL"

    def test_cache_key_intraday(self) -> None:
        key = _cache_key("TIME_SERIES_INTRADAY", "msft", "5min")
        assert key == "TIME_SERIES_INTRADAY:MSFT:5min"

    def test_cache_key_uppercase(self) -> None:
        """Symbol should be uppercased in the cache key."""
        key = _cache_key("TIME_SERIES_DAILY", "googl")
        assert "GOOGL" in key

    def test_get_cached_miss(self) -> None:
        assert get_cached("nonexistent") is None

    def test_set_and_get_cached(self) -> None:
        data = [{"date": "2025-01-15", "close": 150.0}]
        set_cached("test-key", data)
        result = get_cached("test-key")
        assert result == data

    def test_cache_expiry(self) -> None:
        data = [{"date": "2025-01-15", "close": 150.0}]
        # Manually set with an old timestamp
        _cache["test-key"] = (time.time() - CACHE_TTL - 1, data)
        assert get_cached("test-key") is None
        # Stale entry should be removed
        assert "test-key" not in _cache

    def test_clear_cache(self) -> None:
        set_cached("key1", [{"a": 1}])
        set_cached("key2", [{"b": 2}])
        assert len(_cache) == 2
        clear_cache()
        assert len(_cache) == 0


# ---------------------------------------------------------------------------
# Response parsing tests
# ---------------------------------------------------------------------------


class TestParseTimeSeries:
    """Verify response parsing logic."""

    def test_parses_daily_response(self) -> None:
        raw = _make_daily_response(num_days=3)
        records = _parse_time_series(raw, "Time Series (Daily)")
        assert len(records) == 3
        # Should be sorted ascending
        assert records[0]["date"] < records[1]["date"] < records[2]["date"]

    def test_record_fields(self) -> None:
        raw = _make_daily_response(num_days=1)
        records = _parse_time_series(raw, "Time Series (Daily)")
        record = records[0]
        assert "date" in record
        assert isinstance(record["open"], float)
        assert isinstance(record["high"], float)
        assert isinstance(record["low"], float)
        assert isinstance(record["close"], float)
        assert isinstance(record["volume"], int)

    def test_parses_intraday_response(self) -> None:
        raw = _make_intraday_response(interval="15min", num_points=5)
        records = _parse_time_series(raw, "Time Series (15min)")
        assert len(records) == 5

    def test_raises_on_error_message(self) -> None:
        raw = {"Error Message": "Invalid API call. Something is wrong."}
        with pytest.raises(InvalidTickerError, match="Invalid"):
            _parse_time_series(raw, "Time Series (Daily)")

    def test_raises_on_generic_error(self) -> None:
        raw = {"Error Message": "Some other error occurred"}
        with pytest.raises(ApiError, match="Alpha Vantage API error"):
            _parse_time_series(raw, "Time Series (Daily)")

    def test_raises_on_rate_limit_note(self) -> None:
        raw = {"Note": "Thank you for using Alpha Vantage! Our call frequency limit is 5 calls per minute."}
        with pytest.raises(RateLimitError, match="rate limit"):
            _parse_time_series(raw, "Time Series (Daily)")

    def test_raises_on_rate_limit_information(self) -> None:
        raw = {"Information": "Thank you for using Alpha Vantage! Please visit our premium plan for higher call frequency and more features."}
        with pytest.raises(RateLimitError):
            _parse_time_series(raw, "Time Series (Daily)")

    def test_raises_on_missing_time_series_key(self) -> None:
        raw = {"Meta Data": {"1. Information": "Daily Prices"}}
        with pytest.raises(InvalidTickerError, match="No data found"):
            _parse_time_series(raw, "Time Series (Daily)")

    def test_sorted_ascending(self) -> None:
        """Records should be sorted by date ascending (oldest first)."""
        raw = _make_daily_response(num_days=5)
        records = _parse_time_series(raw, "Time Series (Daily)")
        dates = [r["date"] for r in records]
        assert dates == sorted(dates)


# ---------------------------------------------------------------------------
# fetch_daily tests
# ---------------------------------------------------------------------------


class TestFetchDaily:
    """Verify the fetch_daily function."""

    def test_successful_fetch(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_daily_response()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
        ):
            data = fetch_daily("AAPL")
            assert len(data) == 3
            assert all("date" in r for r in data)

    def test_passes_correct_params(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_daily_response()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response) as mock_get,
        ):
            fetch_daily("AAPL", outputsize="full")
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args
            params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
            assert params["function"] == "TIME_SERIES_DAILY"
            assert params["symbol"] == "AAPL"
            assert params["outputsize"] == "full"
            assert params["apikey"] == "test-api-key-123"

    def test_uppercase_symbol(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_daily_response()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response) as mock_get,
        ):
            fetch_daily("aapl")
            params = mock_get.call_args.kwargs.get("params") or mock_get.call_args[1].get("params")
            assert params["symbol"] == "AAPL"

    def test_uses_cache(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_daily_response()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response) as mock_get,
        ):
            # First call should hit the API
            data1 = fetch_daily("AAPL")
            assert mock_get.call_count == 1

            # Second call should use cache
            data2 = fetch_daily("AAPL")
            assert mock_get.call_count == 1  # Not called again
            assert data1 == data2

    def test_raises_without_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ALPHAVANTAGE_API_KEY", None)
            with pytest.raises(MissingApiKeyError):
                fetch_daily("AAPL")

    def test_handles_connection_error(self, api_key_env: dict[str, str]) -> None:
        with (
            patch.dict(os.environ, api_key_env),
            patch(
                "tools.alpha_vantage.requests.get",
                side_effect=requests.ConnectionError("Connection refused"),
            ),
        ):
            with pytest.raises(ApiError, match="Network error"):
                fetch_daily("AAPL")

    def test_handles_timeout(self, api_key_env: dict[str, str]) -> None:
        with (
            patch.dict(os.environ, api_key_env),
            patch(
                "tools.alpha_vantage.requests.get",
                side_effect=requests.Timeout("Timed out"),
            ),
        ):
            with pytest.raises(ApiError, match="timed out"):
                fetch_daily("AAPL")

    def test_handles_http_error(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            response=mock_response
        )

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
        ):
            with pytest.raises(ApiError, match="HTTP error"):
                fetch_daily("AAPL")

    def test_invalid_ticker(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Error Message": "Invalid API call. Please retry or check the documentation."
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
        ):
            with pytest.raises(InvalidTickerError):
                fetch_daily("INVALIDTICKER")

    def test_rate_limit(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Note": "Thank you for using Alpha Vantage! Our call frequency limit is reached."
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
        ):
            with pytest.raises(RateLimitError):
                fetch_daily("AAPL")


# ---------------------------------------------------------------------------
# fetch_intraday tests
# ---------------------------------------------------------------------------


class TestFetchIntraday:
    """Verify the fetch_intraday function."""

    def test_successful_fetch(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_intraday_response()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
        ):
            data = fetch_intraday("AAPL")
            assert len(data) == 3

    def test_passes_correct_params(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_intraday_response(interval="15min")
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response) as mock_get,
        ):
            fetch_intraday("MSFT", interval="15min")
            params = mock_get.call_args.kwargs.get("params") or mock_get.call_args[1].get("params")
            assert params["function"] == "TIME_SERIES_INTRADAY"
            assert params["symbol"] == "MSFT"
            assert params["interval"] == "15min"

    @pytest.mark.parametrize("interval", VALID_INTERVALS)
    def test_all_valid_intervals(
        self, interval: str, api_key_env: dict[str, str]
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_intraday_response(interval=interval)
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
        ):
            data = fetch_intraday("AAPL", interval=interval)
            assert isinstance(data, list)

    def test_invalid_interval(self, api_key_env: dict[str, str]) -> None:
        with patch.dict(os.environ, api_key_env):
            with pytest.raises(ValueError, match="Invalid interval"):
                fetch_intraday("AAPL", interval="2min")

    def test_uses_cache(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_intraday_response()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response) as mock_get,
        ):
            data1 = fetch_intraday("AAPL", interval="5min")
            data2 = fetch_intraday("AAPL", interval="5min")
            assert mock_get.call_count == 1
            assert data1 == data2

    def test_different_intervals_not_cached(self, api_key_env: dict[str, str]) -> None:
        """Different intervals should have separate cache entries."""
        mock_response_5 = MagicMock()
        mock_response_5.json.return_value = _make_intraday_response(interval="5min")
        mock_response_5.raise_for_status = MagicMock()

        mock_response_15 = MagicMock()
        mock_response_15.json.return_value = _make_intraday_response(interval="15min")
        mock_response_15.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch(
                "tools.alpha_vantage.requests.get",
                side_effect=[mock_response_5, mock_response_15],
            ) as mock_get,
        ):
            fetch_intraday("AAPL", interval="5min")
            fetch_intraday("AAPL", interval="15min")
            assert mock_get.call_count == 2

    def test_raises_without_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ALPHAVANTAGE_API_KEY", None)
            with pytest.raises(MissingApiKeyError):
                fetch_intraday("AAPL")

    def test_handles_network_error(self, api_key_env: dict[str, str]) -> None:
        with (
            patch.dict(os.environ, api_key_env),
            patch(
                "tools.alpha_vantage.requests.get",
                side_effect=requests.ConnectionError("No connection"),
            ),
        ):
            with pytest.raises(ApiError, match="Network error"):
                fetch_intraday("AAPL")


# ---------------------------------------------------------------------------
# Error hierarchy tests
# ---------------------------------------------------------------------------


class TestErrorHierarchy:
    """Verify the error class hierarchy."""

    def test_missing_api_key_is_alpha_vantage_error(self) -> None:
        assert issubclass(MissingApiKeyError, AlphaVantageError)

    def test_invalid_ticker_is_alpha_vantage_error(self) -> None:
        assert issubclass(InvalidTickerError, AlphaVantageError)

    def test_rate_limit_is_alpha_vantage_error(self) -> None:
        assert issubclass(RateLimitError, AlphaVantageError)

    def test_api_error_is_alpha_vantage_error(self) -> None:
        assert issubclass(ApiError, AlphaVantageError)

    def test_base_is_exception(self) -> None:
        assert issubclass(AlphaVantageError, Exception)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCli:
    """Verify the CLI interface."""

    def test_daily_command(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_daily_response()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
            patch("sys.argv", ["alpha_vantage", "daily", "AAPL"]),
            patch("builtins.print") as mock_print,
        ):
            from tools.alpha_vantage import main

            main()
            # Should print JSON output
            mock_print.assert_called_once()
            output = mock_print.call_args[0][0]
            parsed = json.loads(output)
            assert isinstance(parsed, list)
            assert len(parsed) == 3

    def test_intraday_command(self, api_key_env: dict[str, str]) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _make_intraday_response(interval="15min")
        mock_response.raise_for_status = MagicMock()

        with (
            patch.dict(os.environ, api_key_env),
            patch("tools.alpha_vantage.requests.get", return_value=mock_response),
            patch(
                "sys.argv",
                ["alpha_vantage", "intraday", "AAPL", "--interval", "15min"],
            ),
            patch("builtins.print") as mock_print,
        ):
            from tools.alpha_vantage import main

            main()
            mock_print.assert_called_once()
            output = mock_print.call_args[0][0]
            parsed = json.loads(output)
            assert isinstance(parsed, list)

    def test_no_args_exits(self) -> None:
        with (
            patch("sys.argv", ["alpha_vantage"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            from tools.alpha_vantage import main

            main()
        assert exc_info.value.code == 1

    def test_unknown_command_exits(self) -> None:
        with (
            patch("sys.argv", ["alpha_vantage", "unknown"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            from tools.alpha_vantage import main

            main()
        assert exc_info.value.code == 1

    def test_daily_no_symbol_exits(self) -> None:
        with (
            patch("sys.argv", ["alpha_vantage", "daily"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            from tools.alpha_vantage import main

            main()
        assert exc_info.value.code == 1

    def test_intraday_no_symbol_exits(self) -> None:
        with (
            patch("sys.argv", ["alpha_vantage", "intraday"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            from tools.alpha_vantage import main

            main()
        assert exc_info.value.code == 1
