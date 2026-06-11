#!/usr/bin/env python3
"""
Pull historical bars from IBKR by walking backwards in chunks until data runs out.

Useful for assembling intraday time series for backtesting or vol analysis.
For 5-min bars, IBKR can only return ~1 month per request, so this script chunks
automatically and paces requests to stay under IBKR's 60-per-10-min limit.

Usage:
    # 5-min bars going as far back as IBKR allows for GOOGL
    python3 pull_history.py GOOGL

    # Daily bars from 2015 — single request, finishes in seconds
    python3 pull_history.py GOOGL --bar 1d --start 2015-01-01

    # 1-min bars, last 30 days, regular trading hours only
    python3 pull_history.py GOOGL --bar 1m --start 2026-05-01 --rth

    # Multiple tickers (downloaded serially because of pacing)
    python3 pull_history.py GOOGL AAPL NVDA --bar 5m --start 2025-01-01

    # Custom output file
    python3 pull_history.py GOOGL --bar 5m --out googl_5m.csv

Output:
    One CSV per ticker (default: <ticker>_<bar>.csv) with columns:
    date, open, high, low, close, volume, avg_price, bar_count

Notes:
    - --bar accepts: 1s, 5s, 10s, 15s, 30s, 1m, 2m, 3m, 5m, 10m, 15m, 20m, 30m, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1M
    - For 5-min bars, retail accounts typically see 1-2 years back; with HMDS subscription, more.
    - For 1-min bars, depth is shorter (~6 months).
    - For daily bars, IBKR usually returns full history in one call.
    - The script stops automatically when IBKR returns 0 bars (i.e. it walked past the depth limit).
    - Press Ctrl+C to abort cleanly — partial CSV is saved.

IBKR pacing safety:
    Default --pause is 10 seconds between requests (~6 req/min, well under the 60/10min limit).
    Don't lower this unless you know what you're doing — you can get throttled.
"""

import argparse
import csv
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from ib_insync import IB, Stock, util
except ImportError:
    print("ERROR: ib_insync not installed. Run: pip3 install ib_insync")
    sys.exit(1)

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

util.startLoop()

_stop_requested = False


def _handle_sigint(sig, frame):
    global _stop_requested
    print("\n  ⏹  Stop requested — finishing current chunk, then saving.")
    _stop_requested = True


signal.signal(signal.SIGINT, _handle_sigint)


# ==================== BAR SIZE → IBKR STRINGS ====================
# Map user-friendly bar codes → (IBKR barSizeSetting, max durationStr per request)
BAR_MAP = {
    '1s':  ('1 secs',   '1800 S'),   # 30 min of 1s bars per request
    '5s':  ('5 secs',   '3600 S'),   # 1 hour
    '10s': ('10 secs',  '14400 S'),  # 4 hours
    '15s': ('15 secs',  '14400 S'),
    '30s': ('30 secs',  '28800 S'),  # 8 hours
    '1m':  ('1 min',    '1 D'),      # 1 day per request (390 bars)
    '2m':  ('2 mins',   '2 D'),
    '3m':  ('3 mins',   '1 W'),
    '5m':  ('5 mins',   '1 M'),      # ~1 month per request (~1700 bars)
    '10m': ('10 mins',  '1 M'),
    '15m': ('15 mins',  '1 M'),
    '20m': ('20 mins',  '1 M'),
    '30m': ('30 mins',  '1 M'),
    '1h':  ('1 hour',   '1 Y'),      # 1 year per request
    '2h':  ('2 hours',  '1 Y'),
    '3h':  ('3 hours',  '1 Y'),
    '4h':  ('4 hours',  '1 Y'),
    '8h':  ('8 hours',  '1 Y'),
    '1d':  ('1 day',    '30 Y'),     # All available in one shot
    '1w':  ('1 week',   '30 Y'),
    '1M':  ('1 month',  '30 Y'),
}


# Map durationStr → timedelta to advance the walk-back cursor
DURATION_TO_DAYS = {
    '1800 S':    0.5/24,     # 30 min
    '3600 S':    1/24,
    '14400 S':   4/24,
    '28800 S':   8/24,
    '1 D':       1,
    '2 D':       2,
    '1 W':       7,
    '1 M':       30,
    '1 Y':       365,
    '30 Y':      30 * 365,
}


def step_back_days(duration_str):
    return DURATION_TO_DAYS.get(duration_str, 30)


# ==================== FETCH LOOP ====================
def fetch_history(ib, ticker, bar_code, start_date, end_date, use_rth, what_to_show, pause_sec):
    """Walk backwards from end_date until reaching start_date (or IBKR returns nothing)."""
    bar_size, dur = BAR_MAP[bar_code]
    step_days = step_back_days(dur)

    print(f"\n  ── Fetching {ticker} {bar_size} bars ──")
    print(f"  Range:   {start_date.date()} → {end_date.date()}")
    print(f"  Chunk:   {dur} ({step_days:.1f} days)  ·  pause {pause_sec}s between chunks")
    print(f"  RTH:     {'yes' if use_rth else 'no (includes pre/post market)'}")
    print(f"  What:    {what_to_show}")

    stock = Stock(ticker, 'SMART', 'USD')
    if not ib.qualifyContracts(stock):
        print(f"  ✗ Failed to qualify {ticker}")
        return []

    cursor = end_date
    all_bars = []
    chunk_num = 0
    consecutive_empty = 0

    while cursor > start_date and not _stop_requested:
        chunk_num += 1
        end_str = cursor.strftime('%Y%m%d %H:%M:%S')
        print(f"  → chunk {chunk_num}: ending {cursor.strftime('%Y-%m-%d %H:%M')}... ", end='', flush=True)
        try:
            bars = ib.reqHistoricalData(
                stock,
                endDateTime=end_str,
                durationStr=dur,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=use_rth,
                formatDate=1,
                keepUpToDate=False,
            )
        except Exception as e:
            print(f"error — {e}")
            time.sleep(pause_sec)
            continue

        if not bars:
            consecutive_empty += 1
            print(f"0 bars (empty)")
            if consecutive_empty >= 2:
                print(f"  ⚠ Two empty chunks in a row — assuming we hit IBKR's depth limit. Stopping.")
                break
            # try walking back one more chunk in case of a holiday gap
            cursor = cursor - timedelta(days=step_days)
            time.sleep(pause_sec)
            continue

        consecutive_empty = 0
        oldest = bars[0].date
        newest = bars[-1].date
        print(f"{len(bars):>5} bars  (oldest: {oldest})")
        all_bars.extend(bars)

        # Walk cursor back to before this chunk's oldest bar.
        # ib_insync returns tz-aware datetimes for intraday bars; strip the tz so
        # comparisons with naive start_date/end_date don't blow up.
        if isinstance(oldest, datetime):
            cursor = oldest.replace(tzinfo=None) if oldest.tzinfo else oldest
        else:
            # date-only object (1d / 1w / 1M bars)
            cursor = datetime.combine(oldest, datetime.min.time())

        # Stop if we've gone past start_date
        if cursor <= start_date:
            print(f"  ✓ Reached start_date. Done.")
            break

        time.sleep(pause_sec)

    # Dedupe by (date) — IBKR can return overlapping bars at chunk boundaries
    seen = set()
    deduped = []
    for b in all_bars:
        k = b.date
        if k in seen:
            continue
        seen.add(k)
        deduped.append(b)
    deduped.sort(key=lambda b: b.date)

    print(f"  ✓ {ticker}: {len(deduped)} unique bars over {chunk_num} requests")
    return deduped


def write_csv(bars, out_path):
    if not bars:
        print(f"  (no bars to write to {out_path})")
        return
    with open(out_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['date', 'open', 'high', 'low', 'close', 'volume', 'avg_price', 'bar_count'])
        for b in bars:
            w.writerow([
                b.date,
                b.open, b.high, b.low, b.close,
                b.volume,
                getattr(b, 'average', None),
                getattr(b, 'barCount', None),
            ])
    print(f"  💾 wrote {len(bars)} rows → {out_path}")


# ==================== MAIN ====================
def parse_date(s):
    """Accept 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' or 'today'."""
    if s.lower() == 'today':
        return datetime.now()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date '{s}'. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.")


def main():
    parser = argparse.ArgumentParser(
        description='Pull historical IBKR bars in chunks. For 5-min bars, walks backward 1-month at a time.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('tickers', nargs='+', help='One or more stock symbols (e.g. GOOGL AAPL)')
    parser.add_argument('--bar', default='5m', choices=list(BAR_MAP.keys()),
                        help='Bar size (default 5m). Supported: ' + ', '.join(BAR_MAP.keys()))
    parser.add_argument('--start', type=str, default='2015-01-01',
                        help='Start date YYYY-MM-DD (default 2015-01-01). Script may stop earlier if IBKR has no data.')
    parser.add_argument('--end', type=str, default='today',
                        help="End date YYYY-MM-DD (default 'today').")
    parser.add_argument('--rth', action='store_true',
                        help='Regular trading hours only. Default: include pre/post market.')
    parser.add_argument('--what', default='TRADES',
                        choices=['TRADES', 'MIDPOINT', 'BID', 'ASK', 'BID_ASK', 'HISTORICAL_VOLATILITY', 'OPTION_IMPLIED_VOLATILITY'],
                        help='What to fetch (default TRADES).')
    parser.add_argument('--pause', type=float, default=10.0,
                        help='Seconds to pause between chunked requests (default 10). Below 5 risks getting throttled.')
    parser.add_argument('--out', type=str, default=None,
                        help='Output CSV path. Default: <ticker>_<bar>.csv. Ignored when multiple tickers.')
    parser.add_argument('--out-dir', type=str, default='.',
                        help='Output directory (default current dir).')
    parser.add_argument('--paper', action='store_true', help='Paper trading (port 4002)')
    parser.add_argument('--port', type=int, default=None, help='Custom IBKR port')
    parser.add_argument('--client-id', type=int, default=53, help='IBKR API client ID')
    args = parser.parse_args()

    tickers = [t.upper() for t in args.tickers]
    start_date = parse_date(args.start)
    end_date = parse_date(args.end)
    if start_date >= end_date:
        print(f"  ✗ start ({start_date}) must be before end ({end_date})")
        sys.exit(1)

    port = args.port or (4002 if args.paper else 4001)
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    bar_size, dur = BAR_MAP[args.bar]
    days_back = (end_date - start_date).days
    estimated_chunks = max(1, int(days_back / step_back_days(dur)))
    estimated_seconds = estimated_chunks * args.pause

    print(f"╔════════════════════════════════════════════════════════════╗")
    print(f"║  IBKR Historical Bar Puller")
    print(f"║  Tickers:   {', '.join(tickers)}")
    print(f"║  Bar size:  {bar_size}  (chunk size: {dur})")
    print(f"║  Range:     {start_date.date()} → {end_date.date()}  ({days_back} days)")
    print(f"║  Estimate:  ~{estimated_chunks} chunks/ticker × {args.pause}s = ~{estimated_seconds/60:.1f} min/ticker")
    print(f"║  Output:    {out_dir}/")
    print(f"║  IBKR port: {port}")
    print(f"╚════════════════════════════════════════════════════════════╝")

    if estimated_chunks > 30:
        print(f"\n  ⚠ This is a long-running download (~{estimated_seconds/60:.0f} min per ticker × {len(tickers)} tickers).")
        print(f"    You can Ctrl+C anytime; partial CSV is saved.")

    print(f"\n  Connecting to IBKR on port {port}...", end='', flush=True)
    ib = IB()
    try:
        ib.connect('127.0.0.1', port, clientId=args.client_id, timeout=15, readonly=True)
    except Exception as e:
        print(f"\n  ✗ {e}\n  Is IB Gateway running and logged in?")
        sys.exit(1)
    print(" ok")
    ib.reqMarketDataType(2)  # frozen — historical doesn't need live

    try:
        for tkr in tickers:
            if _stop_requested:
                break
            bars = fetch_history(
                ib, tkr, args.bar, start_date, end_date,
                use_rth=args.rth, what_to_show=args.what, pause_sec=args.pause,
            )
            if args.out and len(tickers) == 1:
                out_path = Path(args.out).expanduser().resolve()
            else:
                out_path = out_dir / f"{tkr}_{args.bar}.csv"
            write_csv(bars, out_path)
    finally:
        ib.disconnect()
        print(f"\n  Disconnected.")


if __name__ == '__main__':
    main()
