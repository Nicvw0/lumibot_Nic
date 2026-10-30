#!/usr/bin/env python3
"""
Validation comparative des backtests LumiBot: Yahoo Finance vs Alpaca.
Usage:
    python scripts/validation_backtesting_yahoo_vs_alpaca.py
"""

from datetime import datetime
import json
import os
import pytz
import sys

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from lumibot.credentials import ALPACA_CONFIG
from lumibot.example_strategies.stock_buy_and_hold import BuyAndHold
from lumibot.backtesting import YahooDataBacktesting, AlpacaBacktesting


def run_test(source_name, datasource_class, start_dt, end_dt, extra_kwargs=None):
    kwargs = {
        "datasource_class": datasource_class,
        "backtesting_start": start_dt,
        "backtesting_end": end_dt,
        "benchmark_asset": "SPY",
        "show_plot": False,
        "save_tearsheet": False,
        "show_progress_bar": False,
        "parameters": {"buy_symbol": "SPY"},
    }
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    t0 = datetime.now()
    results, strategy = BuyAndHold.run_backtest(**kwargs)
    elapsed = (datetime.now() - t0).total_seconds()

    return {
        "source": source_name,
        "final_value": strategy.portfolio_value,
        "elapsed_seconds": elapsed,
        "results": results,
    }


def main():
    tz = pytz.timezone("America/New_York")
    start = tz.localize(datetime(2024, 1, 1))
    end = tz.localize(datetime(2025, 1, 1))

    print("=" * 60)
    print("VALIDATION COMPARATIVE LUMIBOT: YAHOO FINANCE vs ALPACA")
    print(f"Période: {start.date()} -> {end.date()} | Actif: SPY | Capital: 100,000 USD")
    print("=" * 60)

    # 1. Test Yahoo Finance
    print("\n[1/2] Exécution du backtest Yahoo Finance (Raw unadjusted)...")
    res_yahoo = run_test(
        "Yahoo Finance",
        YahooDataBacktesting,
        start,
        end,
    )
    print(f"  -> Terminé en {res_yahoo['elapsed_seconds']:.2f}s | Valeur finale: {res_yahoo['final_value']:,.2f} $")

    # 2. Test Alpaca (auto_adjust=True, default in AlpacaBacktesting)
    print("\n[2/2] Exécution du backtest Alpaca (SIP Feed, Total Return Adjusted)...")
    res_alpaca = run_test(
        "Alpaca (Adjusted)",
        AlpacaBacktesting,
        start,
        end,
        extra_kwargs={
            "timestep": "day",
            "market": "NYSE",
            "config": ALPACA_CONFIG,
            "auto_adjust": True,
            "full_window": True,
        },
    )
    print(f"  -> Terminé en {res_alpaca['elapsed_seconds']:.2f}s | Valeur finale: {res_alpaca['final_value']:,.2f} $")

    print("\n" + "=" * 60)
    print("RÉCAPITULATIF COMPARATIF")
    print("=" * 60)
    print(f"Yahoo Finance : {res_yahoo['final_value']:,.2f} $ (+{(res_yahoo['final_value']/100000 - 1)*100:.2f}%)")
    print(f"Alpaca        : {res_alpaca['final_value']:,.2f} $ (+{(res_alpaca['final_value']/100000 - 1)*100:.2f}%)")
    print("=" * 60)


if __name__ == "__main__":
    main()
