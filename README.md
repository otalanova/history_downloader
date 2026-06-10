# IBKR Historical Bar Downloader

A small Python script that downloads historical stock prices from your Interactive Brokers account and saves them as a spreadsheet file (CSV).

You give it: a ticker (like GOOGL), a date range, and a bar size (like 1 hour or 5 minutes).
You get: a CSV file with one row per bar, ready to open in Excel or load into a notebook.

This guide assumes you've never used a terminal before. We'll walk through everything.

---

## What you need (one-time setup)

You'll install three things, in this order:

1. **Terminal** — already on your Mac, just need to find it
2. **Python** — the language the script is written in
3. **IB Gateway** — the app that connects Python to your IBKR account

Plan on 15-20 minutes for first-time setup. After that, running the script takes seconds.

---

## Step 1 — Open Terminal

**Terminal** is a built-in Mac app that lets you type commands directly to your computer. It looks like a black or white window where you type text and press Enter.

**To open it:**

1. Press `Cmd + Space` to open Spotlight search
2. Type `Terminal`
3. Press Enter

A window opens with a `$` prompt — you're ready. When this guide says "run this command", it means: copy the line, paste it into Terminal, press Enter.

If you've never seen this before: you can't break anything by reading what's on the screen. Each command you paste does one specific thing, and the output tells you what happened.

---

## Step 2 — Install Python

Python is the programming language that runs this script. macOS comes with a very old version pre-installed; you want a current one.

**First, check what you have.** In Terminal, run:

```bash
python3 --version
```

- If it says `Python 3.10.x` or higher (3.11, 3.12, 3.13 are all fine) → you're done with this step, skip to Step 3.
- If it says `Python 3.9.x` or lower, or "command not found" → install a newer version below.

**To install Python:**

1. Go to **[python.org/downloads](https://www.python.org/downloads/)**
2. Click the big yellow "Download Python 3.x.x" button at the top
3. Open the downloaded `.pkg` file and click through the installer (all defaults are fine)
4. Close and reopen Terminal, then run `python3 --version` again to confirm it worked

---

## Step 3 — Install the script's library

The script depends on one external Python library called `ib_insync`. Install it by running:

```bash
pip3 install ib_insync
```

You'll see a few lines about downloading and installing. When you get the `$` prompt back, it's done.

(If you see a "permission denied" or "externally-managed-environment" error, try `pip3 install ib_insync --break-system-packages` instead.)

---

## Step 4 — Install and set up IB Gateway

**IB Gateway** is a free desktop app from Interactive Brokers. It runs in the background, holds your IBKR login, and lets Python read data from your account. The script can't connect to IBKR without it.

### 4a. Download

Go to **[interactivebrokers.com → IB Gateway Stable](https://www.interactivebrokers.com/en/trading/ib-gateway-stable.php)** and download the Mac version. Install it like any other Mac app (drag to Applications).

### 4b. Log in

1. Open IB Gateway from Applications
2. Choose **"IB API"** (not FIX) when it asks for the connection type
3. Choose **"Live Trading"** (or "Paper Trading" if you want practice data)
4. Enter your normal IBKR username and password
5. After login, you should see a small window saying "Connected"

Leave this window open in the background. The script needs it running.

### 4c. Enable API access (only needed once)

In IB Gateway, click **Configure → Settings → API → Settings** and set:

- ✅ **Enable ActiveX and Socket Clients** — check this on
- **Socket port**: `4001` for Live Trading, `4002` for Paper Trading
- **Master API client ID**: `0`
- **Trusted IPs**: add `127.0.0.1` (this means "this computer only")
- ❌ **Read-Only API**: leave this **OFF** (the script handles read-only safety on its own; the GUI checkbox causes errors)
- ✅ **Allow connections from localhost only** — check this on (security)

Click OK to save. You only do this configuration once — it's remembered next time.

---

## Step 5 — Run the script

The script (`pull_history.py`) lives inside this `history_downloader` folder. Before you can run it, you need to tell Terminal "go into that folder". Then you tell Terminal "now run the script". Two separate commands.

### 5a. Find where the folder is on your computer

This sounds silly, but it's the step that trips people up.

- If you **downloaded a ZIP from GitHub**, by default it went to your **Downloads folder**, and there'll be a folder called something like `history_downloader-main` inside it.
- If someone **shared the folder with you** (Dropbox, AirDrop, USB), it's wherever you saved it.
- If you **cloned with git**, it's in whichever folder you ran `git clone` from.

Just open Finder and locate the `history_downloader` folder. Note where it is — you don't need to memorize the path, you just need to be able to see the folder.

### 5b. Open Terminal

Press `Cmd + Space`, type `Terminal`, press Enter. (Same as Step 1.)

### 5c. Tell Terminal to go into that folder (the drag trick)

This is the easiest way and it works every time. Do these steps in order:

1. In Terminal, type exactly this — including the space at the end, and **do not press Enter yet**:

   ```
   cd 
   ```

2. Now switch to Finder.
3. Click and **drag** the `history_downloader` folder from Finder onto your Terminal window, then let go.
4. Terminal will automatically fill in the full path. You should see something like:

   ```
   cd /Users/yourname/Downloads/history_downloader 
   ```

5. **Now** press Enter.

You should see your prompt change — the part before the `$` now shows the folder name, like `otalanova@olgas-mac history_downloader %`.

### 5d. Verify you're in the right place

Type `ls` (lowercase L, lowercase S) and press Enter. You should see:

```
README.md  pull_history.py  requirements.txt
```

If you see those three files, you're in the right place and ready to run the script.

If you see something else (a different file list, or "ls: No such file...") — you're in the wrong folder. Repeat step 5c.

### 5e. Run the script — hourly Google bars for all of 2026

```bash
python3 pull_history.py GOOGL --bar 1h --start 2026-01-01 --end 2026-12-31
```

What this means, piece by piece:

| Part | Meaning |
|---|---|
| `python3` | Run Python |
| `pull_history.py` | The script |
| `GOOGL` | The stock ticker (use `GOOGL` for Google class A, `GOOG` for class C — they trade slightly differently) |
| `--bar 1h` | One bar per hour |
| `--start 2026-01-01` | First date to download |
| `--end 2026-12-31` | Last date to download |

When you press Enter, you'll see something like:

```
╔════════════════════════════════════════════════════════════╗
║  IBKR Historical Bar Puller
║  Tickers:   GOOGL
║  Bar size:  1 hour  (chunk size: 1 Y)
║  Range:     2026-01-01 → 2026-12-31  (364 days)
║  ...
  Connecting to IBKR on port 4001... ok
  → chunk 1: ending 2026-12-31 23:59...  1632 bars  (oldest: 2026-01-02)
  ✓ GOOGL: 1632 unique bars over 1 requests
  💾 wrote 1632 rows → GOOGL_1h.csv
  Disconnected.
```

Done. You now have a file called **`GOOGL_1h.csv`** in this folder, with one row per trading hour of 2026.

### 5f. Where to find the CSV

The CSV is saved **inside the same `history_downloader` folder** that the script is in. To open it:

- **In Finder**: open the `history_downloader` folder; double-click `GOOGL_1h.csv` — it'll open in Excel or Numbers.
- **From Terminal**: run `open GOOGL_1h.csv` and it'll launch in your default spreadsheet app.

The columns are: `date, open, high, low, close, volume, avg_price, bar_count`.

---

## Quick reminder for next time

Once everything is installed, running the script again is just three things:

1. Make sure **IB Gateway** is open and logged in (Step 4b)
2. Open Terminal, `cd` into the `history_downloader` folder (Step 5c — the drag trick)
3. Run a `python3 pull_history.py ...` command

You don't need to repeat Steps 2, 3, or 4c again — they're one-time setup.

---

## A few more useful examples

```bash
# Daily bars going back to 2015 — fast, one API call
python3 pull_history.py GOOGL --bar 1d --start 2015-01-01

# 5-minute bars (will go back as far as your IBKR account allows; usually 1-2 years)
python3 pull_history.py GOOGL --bar 5m

# Several tickers at once
python3 pull_history.py GOOGL AAPL NVDA --bar 1h --start 2026-01-01

# Only during regular trading hours (no pre-market or after-hours)
python3 pull_history.py GOOGL --bar 1h --start 2026-01-01 --rth
```

To stop a long-running download, press `Ctrl + C` in Terminal — it'll finish the current chunk and save what it has.

---

## Bar sizes you can use

Pass any of these as `--bar`:

`1s`, `5s`, `10s`, `15s`, `30s`, `1m`, `2m`, `3m`, `5m`, `10m`, `15m`, `20m`, `30m`, `1h`, `2h`, `3h`, `4h`, `8h`, `1d` (daily), `1w` (weekly), `1M` (monthly)

Smaller bars = more rows = longer to download. Daily bars are essentially free; 5-minute bars over many years can take 20+ minutes.

---

## If something goes wrong

| What you see | What it means / what to do |
|---|---|
| `command not found: python3` | Python isn't installed. Redo Step 2. |
| `ModuleNotFoundError: No module named 'ib_insync'` | The library isn't installed. Redo Step 3. |
| `Connection failed` or `connection refused` | IB Gateway isn't running, or you're not logged in. Open it, log in, wait for "Connected", then re-run. |
| `0 bars (empty)` early in the download | Your IBKR account doesn't have data that far back for this bar size. Try `--bar 1d` (daily) or a more recent `--start` date. |
| Script seems frozen for 30+ seconds | IBKR is rate-limiting. Press Ctrl+C, wait a minute, re-run with `--pause 15`. |
| Anything else | Read the error message — it usually tells you what's wrong. If stuck, copy the error and ask Claude. |

---

## Is this safe?

Yes. The script connects to IBKR in **read-only mode** — it can pull data but cannot place trades, modify positions, or move money. There is no way for it to do anything but download CSV files.

Your IBKR password lives only in IB Gateway. The script never sees it.
