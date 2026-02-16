"""Alpha Vantage API client for fetching stock market data.

This module provides functions to fetch daily and intraday time series data
from the Alpha Vantage API. It includes:
- Session-level caching to avoid redundant API calls
- Structured data output suitable for Plotly charting
- Clear error handling for common failure modes

Usage as a CLI tool (for the agent to call via Bash):
    python -m tools.alpha_vantage daily AAPL
    python -m tools.alpha_vantage intraday AAPL --interval 15min

Usage as a Python module:
    from tools.alpha_vantage import fetch_daily, fetch_intraday
    data = fetch_daily("AAPL")
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://www.alphavantage.co/query"
"""Alpha Vantage API base URL."""

VALID_INTERVALS = ("1min", "5min", "15min", "30min", "60min")
"""Supported intraday intervals."""

REQUEST_TIMEOUT = 30
"""HTTP request timeout in seconds."""

# ---------------------------------------------------------------------------
# Session-level cache
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
"""In-memory cache mapping cache keys to (timestamp, data) tuples."""

CACHE_TTL = 300
"""Cache time-to-live in seconds (5 minutes)."""


def _cache_key(function: str, symbol: str, interval: str | None = None) -> str:
    """Generate a cache key for a given request.

    Parameters
    ----------
    function:
        The API function (e.g., "TIME_SERIES_DAILY").
    symbol:
        The stock ticker symbol.
    interval:
        The intraday interval (only for intraday requests).

    Returns
    -------
    str
        A unique cache key string.
    """
    parts = [function, symbol.upper()]
    if interval:
        parts.append(interval)
    return ":".join(parts)


def get_cached(key: str) -> list[dict[str, Any]] | None:
    """Retrieve cached data if it exists and hasn't expired.

    Parameters
    ----------
    key:
        The cache key to look up.

    Returns
    -------
    list[dict[str, Any]] | None
        The cached data, or None if not found or expired.
    """
    if key in _cache:
        timestamp, data = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return data
        # Expired — remove stale entry
        del _cache[key]
    return None


def set_cached(key: str, data: list[dict[str, Any]]) -> None:
    """Store data in the cache with the current timestamp.

    Parameters
    ----------
    key:
        The cache key.
    data:
        The data to cache.
    """
    _cache[key] = (time.time(), data)


def clear_cache() -> None:
    """Clear all cached data."""
    _cache.clear()


# ---------------------------------------------------------------------------
# Error classes
# ---------------------------------------------------------------------------


class AlphaVantageError(Exception):
    """Base exception for Alpha Vantage API errors."""


class MissingApiKeyError(AlphaVantageError):
    """Raised when the ALPHAVANTAGE_API_KEY is not configured."""


class InvalidTickerError(AlphaVantageError):
    """Raised when the API returns no data for a given ticker symbol."""


class RateLimitError(AlphaVantageError):
    """Raised when the Alpha Vantage rate limit has been exceeded."""


class ApiError(AlphaVantageError):
    """Raised for general API errors (network, unexpected responses)."""


# ---------------------------------------------------------------------------
# API key validation
# ---------------------------------------------------------------------------


def _get_api_key() -> str:
    """Retrieve and validate the Alpha Vantage API key from environment.

    Returns
    -------
    str
        The API key.

    Raises
    ------
    MissingApiKeyError
        If ALPHAVANTAGE_API_KEY is not set or empty.
    """
    key = os.environ.get("ALPHAVANTAGE_API_KEY", "").strip()
    if not key:
        raise MissingApiKeyError(
            "ALPHAVANTAGE_API_KEY is not set. "
            "Please add it to your .env file or set it as an environment variable. "
            "Get a free key at https://www.alphavantage.co/support/#api-key"
        )
    return key


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


def _parse_time_series(
    raw_data: dict[str, Any],
    time_series_key: str,
) -> list[dict[str, Any]]:
    """Parse Alpha Vantage time series response into structured records.

    Parameters
    ----------
    raw_data:
        The raw JSON response from the API.
    time_series_key:
        The key in the response containing the time series data
        (e.g., "Time Series (Daily)").

    Returns
    -------
    list[dict[str, Any]]
        A list of dicts with keys: date, open, high, low, close, volume.
        Sorted by date ascending (oldest first).

    Raises
    ------
    InvalidTickerError
        If the time series key is not found in the response.
    RateLimitError
        If the API indicates a rate limit has been hit.
    ApiError
        If the response contains an error message.
    """
    # Check for API error messages
    if "Error Message" in raw_data:
        error_msg = raw_data["Error Message"]
        if "Invalid API call" in error_msg or "invalid" in error_msg.lower():
            raise InvalidTickerError(
                f"Invalid ticker symbol or API parameters: {error_msg}"
            )
        raise ApiError(f"Alpha Vantage API error: {error_msg}")

    if "Note" in raw_data:
        note = raw_data["Note"]
        if "call frequency" in note.lower() or "rate limit" in note.lower():
            raise RateLimitError(
                "Alpha Vantage rate limit exceeded. "
                "Free tier allows 25 requests/day and 5 requests/minute. "
                "Please wait and try again."
            )

    if "Information" in raw_data:
        info = raw_data["Information"]
        if "rate limit" in info.lower() or "call frequency" in info.lower():
            raise RateLimitError(
                "Alpha Vantage rate limit exceeded. "
                "Free tier allows 25 requests/day and 5 requests/minute. "
                "Please wait and try again."
            )
        if "premium" in info.lower() or "subscribe" in info.lower():
            raise RateLimitError(
                f"Alpha Vantage API limit reached: {info}"
            )

    if time_series_key not in raw_data:
        raise InvalidTickerError(
            f"No data found. The ticker symbol may be invalid or the API "
            f"returned an unexpected response. Response keys: {list(raw_data.keys())}"
        )

    time_series = raw_data[time_series_key]
    records: list[dict[str, Any]] = []

    for date_str, values in time_series.items():
        records.append(
            {
                "date": date_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
            }
        )

    # Sort by date ascending (oldest first) for charting
    records.sort(key=lambda r: r["date"])
    return records


# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------


def fetch_daily(
    symbol: str,
    outputsize: str = "compact",
) -> list[dict[str, Any]]:
    """Fetch daily time series data for a stock symbol.

    Parameters
    ----------
    symbol:
        The stock ticker symbol (e.g., "AAPL", "GOOGL").
    outputsize:
        "compact" (last 100 data points) or "full" (20+ years).
        Defaults to "compact".

    Returns
    -------
    list[dict[str, Any]]
        A list of dicts with keys: date, open, high, low, close, volume.
        Sorted by date ascending.

    Raises
    ------
    MissingApiKeyError
        If the API key is not configured.
    InvalidTickerError
        If the ticker symbol is invalid or no data is returned.
    RateLimitError
        If the API rate limit has been exceeded.
    ApiError
        For network errors or unexpected API responses.
    """
    api_key = _get_api_key()
    symbol = symbol.upper().strip()

    # Check cache
    key = _cache_key("TIME_SERIES_DAILY", symbol)
    cached = get_cached(key)
    if cached is not None:
        return cached

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": api_key,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise ApiError(
            f"Network error: Could not connect to Alpha Vantage API. "
            f"Please check your internet connection. Details: {exc}"
        ) from exc
    except requests.Timeout as exc:
        raise ApiError(
            f"Request timed out after {REQUEST_TIMEOUT} seconds. "
            f"The Alpha Vantage API may be slow. Please try again."
        ) from exc
    except requests.HTTPError as exc:
        raise ApiError(
            f"HTTP error from Alpha Vantage API: {exc.response.status_code} "
            f"{exc.response.reason}"
        ) from exc
    except requests.RequestException as exc:
        raise ApiError(f"Request failed: {exc}") from exc

    raw_data = response.json()
    records = _parse_time_series(raw_data, "Time Series (Daily)")

    # Cache the results
    set_cached(key, records)
    return records


def fetch_intraday(
    symbol: str,
    interval: str = "5min",
    outputsize: str = "compact",
) -> list[dict[str, Any]]:
    """Fetch intraday time series data for a stock symbol.

    Parameters
    ----------
    symbol:
        The stock ticker symbol (e.g., "AAPL", "GOOGL").
    interval:
        The time interval between data points.
        Valid values: "1min", "5min", "15min", "30min", "60min".
        Defaults to "5min".
    outputsize:
        "compact" (last 100 data points) or "full" (full intraday data).
        Defaults to "compact".

    Returns
    -------
    list[dict[str, Any]]
        A list of dicts with keys: date, open, high, low, close, volume.
        Sorted by date ascending.

    Raises
    ------
    ValueError
        If the interval is not one of the valid options.
    MissingApiKeyError
        If the API key is not configured.
    InvalidTickerError
        If the ticker symbol is invalid or no data is returned.
    RateLimitError
        If the API rate limit has been exceeded.
    ApiError
        For network errors or unexpected API responses.
    """
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"Invalid interval '{interval}'. "
            f"Must be one of: {', '.join(VALID_INTERVALS)}"
        )

    api_key = _get_api_key()
    symbol = symbol.upper().strip()

    # Check cache
    key = _cache_key("TIME_SERIES_INTRADAY", symbol, interval)
    cached = get_cached(key)
    if cached is not None:
        return cached

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": api_key,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise ApiError(
            f"Network error: Could not connect to Alpha Vantage API. "
            f"Please check your internet connection. Details: {exc}"
        ) from exc
    except requests.Timeout as exc:
        raise ApiError(
            f"Request timed out after {REQUEST_TIMEOUT} seconds. "
            f"The Alpha Vantage API may be slow. Please try again."
        ) from exc
    except requests.HTTPError as exc:
        raise ApiError(
            f"HTTP error from Alpha Vantage API: {exc.response.status_code} "
            f"{exc.response.reason}"
        ) from exc
    except requests.RequestException as exc:
        raise ApiError(f"Request failed: {exc}") from exc

    raw_data = response.json()
    time_series_key = f"Time Series ({interval})"
    records = _parse_time_series(raw_data, time_series_key)

    # Cache the results
    set_cached(key, records)
    return records


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------


def _cli_daily(args: list[str]) -> None:
    """Handle the 'daily' subcommand."""
    if not args:
        print("Error: Please provide a stock symbol. Usage: daily AAPL", file=sys.stderr)
        sys.exit(1)

    symbol = args[0]
    outputsize = "compact"
    if "--full" in args:
        outputsize = "full"

    try:
        data = fetch_daily(symbol, outputsize=outputsize)
        print(json.dumps(data, indent=2))
    except AlphaVantageError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _cli_intraday(args: list[str]) -> None:
    """Handle the 'intraday' subcommand."""
    if not args:
        print(
            "Error: Please provide a stock symbol. Usage: intraday AAPL --interval 5min",
            file=sys.stderr,
        )
        sys.exit(1)

    symbol = args[0]
    interval = "5min"
    outputsize = "compact"

    # Parse optional flags
    remaining = args[1:]
    i = 0
    while i < len(remaining):
        if remaining[i] == "--interval" and i + 1 < len(remaining):
            interval = remaining[i + 1]
            i += 2
        elif remaining[i] == "--full":
            outputsize = "full"
            i += 1
        else:
            i += 1

    try:
        data = fetch_intraday(symbol, interval=interval, outputsize=outputsize)
        print(json.dumps(data, indent=2))
    except (AlphaVantageError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """CLI entry point for the Alpha Vantage tool.

    Usage:
        python -m tools.alpha_vantage daily AAPL [--full]
        python -m tools.alpha_vantage intraday AAPL [--interval 5min] [--full]
    """
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  python -m tools.alpha_vantage daily SYMBOL [--full]\n"
            "  python -m tools.alpha_vantage intraday SYMBOL [--interval INTERVAL] [--full]\n"
            "\n"
            "Intervals: 1min, 5min, 15min, 30min, 60min\n"
            "Output: JSON array of {date, open, high, low, close, volume}",
            file=sys.stderr,
        )
        sys.exit(1)

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command == "daily":
        _cli_daily(args)
    elif command == "intraday":
        _cli_intraday(args)
    else:
        print(f"Error: Unknown command '{command}'. Use 'daily' or 'intraday'.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
