# IBKR Historical Bar Downloader

A small Python script that downloads historical stock prices from your Interactive Brokers account and saves them as a spreadsheet file (CSV).

You give it: a ticker (like GOOGL), a date range, and a bar size (like 1 hour or 5 minutes).
You get: a CSV file with one row per bar, ready to open in Excel or load into a notebook.

This guide assumes you've never used a terminal before. We'll walk through everything — for both **macOS** and **Windows**. Each step has two versions; just follow the one for your OS.

---

## What you need (one-time setup)

You'll install three things, in this order:

1. **A terminal app** — already on your computer, just need to find it
2. **Python** — the language the script is written in
3. **IB Gateway** — the app that connects Python to your IBKR account

Plan on 15-20 minutes for first-time setup. After that, running the script takes seconds.

---

## Step 1 — Open the terminal

### 🍎 On macOS

The app is called **Terminal**. It's built in.

1. Press `Cmd + Space` to open Spotlight search
2. Type `Terminal`
3. Press Enter

A window opens with a `$` (or `%`) prompt — you're ready.

### 🪟 On Windows

The app is called **PowerShell** (or "Windows PowerShell"). It's built in.

1. Press the `Windows` key (the one with the logo)
2. Type `PowerShell`
3. Press Enter — or right-click and choose "Run as administrator" if you want to be safe with installs

A blue window opens with a `PS C:\Users\YourName>` prompt — you're ready.

> **Tip for Windows:** if you have Windows 11 or recent Windows 10, you can also install the newer **Windows Terminal** app from the Microsoft Store — it's a nicer wrapper around PowerShell. But the built-in PowerShell is perfectly fine.

When this guide says "run this command", it means: copy the line, paste it into the terminal (right-click to paste on Windows), press Enter.

You can't break anything by reading what's on screen. Each command does one specific thing and tells you what happened.

---

## Step 2 — Install Python

### 🍎 On macOS

First, check what you have. In Terminal, run:

```bash
python3 --version
```

- If it says `Python 3.10.x` or higher (3.11, 3.12, 3.13 are all fine) → skip to Step 3.
- If it says `Python 3.9.x` or lower, or "command not found" → install it:

  1. Go to **[python.org/downloads](https://www.python.org/downloads/)**
  2. Click the big yellow "Download Python 3.x.x" button
  3. Open the downloaded `.pkg` file and click through (defaults are fine)
  4. Close and reopen Terminal, then run `python3 --version` again to confirm

### 🪟 On Windows

First, check what you have. In PowerShell, run:

```powershell
python --version
```

- If it says `Python 3.10.x` or higher → skip to Step 3.
- If it says "Python was not found" or shows an old version → install it:

  1. Go to **[python.org/downloads](https://www.python.org/downloads/)**
  2. Click the big yellow "Download Python 3.x.x" button (it auto-detects Windows)
  3. Open the downloaded `.exe` installer
  4. **VERY IMPORTANT: check the box at the bottom of the installer that says ✅ "Add python.exe to PATH"** before clicking Install. Without this, Windows won't know where Python is.
  5. Click "Install Now" and wait for it to finish
  6. Close PowerShell completely (the X in the corner), open a fresh PowerShell window, and run `python --version` again

> If you forgot to check "Add to PATH" during install, the easiest fix is to uninstall Python from Settings → Apps, then reinstall with the box checked.

---

## Step 3 — Install the script's library

The script depends on one external Python library called `ib_insync`.

### 🍎 On macOS

```bash
pip3 install ib_insync
```

(If you see "permission denied" or "externally-managed-environment", try `pip3 install ib_insync --break-system-packages` instead.)

### 🪟 On Windows

```powershell
pip install ib_insync
```

If that fails with "pip is not recognized", use this instead:

```powershell
python -m pip install ib_insync
```

When you get the prompt back without errors, it's installed.

---

## Step 4 — Install and set up IB Gateway

**IB Gateway** is a free desktop app from Interactive Brokers. It runs in the background, holds your IBKR login, and lets Python read data from your account. The script can't connect to IBKR without it.

### 4a. Download and install

Go to **[interactivebrokers.com → IB Gateway Stable](https://www.interactivebrokers.com/en/trading/ib-gateway-stable.php)** and download the version for your OS.

- **macOS** users: download the `.dmg` and drag IB Gateway into Applications.
- **Windows** users: download the `.exe` and run it; click through the installer.

### 4b. Log in

1. Open **IB Gateway** (from Applications on Mac, or the Start menu on Windows)
2. Choose **"IB API"** (not FIX) when it asks for connection type
3. Choose **"Live Trading"** (or "Paper Trading" if you want practice data)
4. Enter your normal IBKR username and password
5. After login, you should see a small window saying "Connected"

Leave this window open in the background. The script needs it running.

### 4c. Enable API access (only needed once)

In IB Gateway, click **Configure → Settings → API → Settings** and set:

- ✅ **Enable ActiveX and Socket Clients** — check this ON
- **Socket port**: `4001` for Live Trading, `4002` for Paper Trading
- **Master API client ID**: `0`
- **Trusted IPs**: add `127.0.0.1`
- ❌ **Read-Only API**: leave this OFF (the script handles read-only safety itself; the GUI checkbox causes errors)
- ✅ **Allow connections from localhost only**

Click OK to save. You only do this configuration once — it's remembered next time.

> **Windows users:** the first time you connect, Windows may pop up a "Firewall" warning. Click **"Allow access"** — the script needs the local port open.

---

## Step 5 — Run the script

The script (`pull_history.py`) lives inside this `history_downloader` folder. Before you can run it, you need to tell the terminal "go into that folder". Then "run the script". Two separate commands.

### 5a. Find where the folder is on your computer

This sounds silly, but it's the step that trips people up.

- If you **downloaded a ZIP from GitHub**, it's in your **Downloads** folder, probably named `history_downloader-main`.
- If someone **shared the folder with you** (Dropbox, AirDrop, USB), it's wherever you saved it.
- If you **cloned with git**, it's in whichever folder you ran `git clone` from.

Open Finder (Mac) or File Explorer (Windows) and locate the `history_downloader` folder. You don't need to memorize the path — you just need to be able to see the folder.

### 5b. Open the terminal

Same as Step 1 — open Terminal (Mac) or PowerShell (Windows).

### 5c. Tell the terminal to go into that folder (the drag trick)

This works the same on both OSes.

#### 🍎 On macOS

1. In Terminal, type `cd ` (the letters c, d, then a space) — **do not press Enter**
2. Switch to Finder
3. **Drag** the `history_downloader` folder from Finder onto your Terminal window, then let go
4. Terminal auto-fills the full path. You should see something like:
   ```
   cd /Users/yourname/Downloads/history_downloader 
   ```
5. **Now** press Enter

Your prompt changes to show the folder name, like `yourname@mac history_downloader %`.

#### 🪟 On Windows

1. In PowerShell, type `cd ` — **do not press Enter**
2. Open File Explorer and find the `history_downloader` folder
3. **Drag** the folder onto your PowerShell window, then let go
4. PowerShell auto-fills the path. You should see something like:
   ```
   cd "C:\Users\YourName\Downloads\history_downloader"
   ```
5. **Now** press Enter

Your prompt changes to show the folder path, like `PS C:\Users\YourName\Downloads\history_downloader>`.

### 5d. Verify you're in the right place

#### 🍎 On macOS

Type `ls` and press Enter. You should see:

```
README.md  pull_history.py  requirements.txt
```

#### 🪟 On Windows

Type `ls` (PowerShell understands it) or `dir`, and press Enter. You should see:

```
README.md
pull_history.py
requirements.txt
```

If you see those three files, you're in the right place. If you see something else, repeat step 5c.

### 5e. Run the script — hourly Google bars for all of 2026

#### 🍎 On macOS

```bash
python3 pull_history.py GOOGL --bar 1h --start 2026-01-01 --end 2026-12-31
```

#### 🪟 On Windows

```powershell
python pull_history.py GOOGL --bar 1h --start 2026-01-01 --end 2026-12-31
```

(Note: macOS uses `python3`, Windows uses `python`. That's the only difference.)

What this means, piece by piece:

| Part | Meaning |
|---|---|
| `python3` / `python` | Run Python |
| `pull_history.py` | The script |
| `GOOGL` | The stock ticker (`GOOGL` = Google class A; `GOOG` = class C — slightly different) |
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

It's saved **inside the same `history_downloader` folder** that the script is in.

#### 🍎 On macOS

- **In Finder**: open the `history_downloader` folder; double-click `GOOGL_1h.csv` — it opens in Excel or Numbers.
- **From Terminal**: run `open GOOGL_1h.csv` to launch it in your default spreadsheet app.

#### 🪟 On Windows

- **In File Explorer**: open the `history_downloader` folder; double-click `GOOGL_1h.csv` — it opens in Excel.
- **From PowerShell**: run `start GOOGL_1h.csv` to launch it in Excel.

The columns are: `date, open, high, low, close, volume, avg_price, bar_count`.

---

## Quick reminder for next time

Once everything is installed, running the script again is just three things:

1. Make sure **IB Gateway** is open and logged in (Step 4b)
2. Open your terminal, `cd` into the `history_downloader` folder (Step 5c — the drag trick)
3. Run a `python3 ...` (Mac) or `python ...` (Windows) command

You don't need to repeat Steps 2, 3, or 4c again — they're one-time setup.

---

## A few more useful examples

(Use `python3` on Mac, `python` on Windows.)

```bash
# Daily bars going back to 2015 — fast, one API call
python3 pull_history.py GOOGL --bar 1d --start 2015-01-01

# 5-minute bars (goes back as far as your IBKR account allows; usually 1-2 years)
python3 pull_history.py GOOGL --bar 5m

# Several tickers at once
python3 pull_history.py GOOGL AAPL NVDA --bar 1h --start 2026-01-01

# Only during regular trading hours (no pre-market or after-hours)
python3 pull_history.py GOOGL --bar 1h --start 2026-01-01 --rth
```

To stop a long-running download, press `Ctrl + C` in the terminal (works the same on Mac and Windows) — it'll finish the current chunk and save what it has.

---

## Bar sizes you can use

Pass any of these as `--bar`:

`1s`, `5s`, `10s`, `15s`, `30s`, `1m`, `2m`, `3m`, `5m`, `10m`, `15m`, `20m`, `30m`, `1h`, `2h`, `3h`, `4h`, `8h`, `1d` (daily), `1w` (weekly), `1M` (monthly)

Smaller bars = more rows = longer to download. Daily bars are essentially free; 5-minute bars over many years can take 20+ minutes.

---

## If something goes wrong

| What you see | What it means / what to do |
|---|---|
| `command not found: python3` (Mac) or `Python was not found` (Windows) | Python isn't installed correctly. Redo Step 2. On Windows, make sure you checked the "Add to PATH" box. |
| `ModuleNotFoundError: No module named 'ib_insync'` | The library isn't installed. Redo Step 3. |
| `'pip' is not recognized` (Windows) | Use `python -m pip install ib_insync` instead. |
| `Connection failed` or `connection refused` | IB Gateway isn't running, or you're not logged in. Open it, log in, wait for "Connected", then re-run. |
| Windows Firewall popup | Click **"Allow access"** — the script needs to connect to IB Gateway on a local port. |
| `0 bars (empty)` early in the download | Your IBKR account doesn't have data that far back for this bar size. Try `--bar 1d` (daily) or a more recent `--start` date. |
| Script seems frozen for 30+ seconds | IBKR is rate-limiting. Press Ctrl+C, wait a minute, re-run with `--pause 15`. |
| Anything else | Read the error message — it usually tells you what's wrong. If stuck, copy the error and ask Claude. |

---

## Is this safe?

Yes. The script connects to IBKR in **read-only mode** — it can pull data but cannot place trades, modify positions, or move money. There is no way for it to do anything but download CSV files.

Your IBKR password lives only in IB Gateway. The script never sees it.
