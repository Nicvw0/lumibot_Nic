#!/usr/bin/env python3
"""
Étape 2 — Validation de la stratégie Momentum originale (stock_momentum.py).

Paramètres :
  - Stratégie : Momentum (lumibot/example_strategies/stock_momentum.py) — NON MODIFIÉ
  - Univers    : SPY, VEU, AGG (valeur par défaut de la stratégie)
  - Période    : 2020-01-01 → 2025-01-01
  - Capital    : 100 000 USD
  - Sources    : AlpacaBacktesting (principal) + YahooDataBacktesting (secondaire)
  - Benchmark  : SPY

Usage :
    $env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
    python scripts/validation_momentum_etape_2.py [--yahoo-only] [--alpaca-only] [--runs N]
"""

import argparse
import os
import sys
import time
from datetime import datetime

import pytz

# ── Chemin vers la racine du dépôt ────────────────────────────────────────────
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ── Imports LumiBot ────────────────────────────────────────────────────────────
from lumibot.backtesting import AlpacaBacktesting, YahooDataBacktesting  # noqa: E402
from lumibot.credentials import ALPACA_CONFIG  # noqa: E402

# IMPORTANT : on importe la stratégie telle quelle, sans la modifier.
from lumibot.example_strategies.stock_momentum import Momentum  # noqa: E402

# ── Configuration ──────────────────────────────────────────────────────────────
TZ = pytz.timezone("America/New_York")
BACKTEST_START = TZ.localize(datetime(2020, 1, 1))
BACKTEST_END = TZ.localize(datetime(2025, 1, 1))
INITIAL_CAPITAL = 100_000
BENCHMARK = "SPY"

# Univers par défaut de la stratégie (défini dans stock_momentum.py ligne 32)
DEFAULT_SYMBOLS = ["SPY", "VEU", "AGG"]

# Paramètres LumiBot communs
COMMON_KWARGS = {
    "backtesting_start": BACKTEST_START,
    "backtesting_end": BACKTEST_END,
    "benchmark_asset": BENCHMARK,
    "initial_cash": INITIAL_CAPITAL,
    "show_plot": False,
    "save_tearsheet": False,
    "show_progress_bar": False,
    # On passe l'univers explicitement, mais la valeur est identique au défaut
    "parameters": {"symbols": DEFAULT_SYMBOLS},
}


# ── Fonction d'exécution d'un backtest ────────────────────────────────────────
def run_backtest(label: str, datasource_class, extra_kwargs: dict | None = None) -> dict:
    """Exécute un backtest et retourne un dictionnaire de résultats."""
    kwargs = dict(COMMON_KWARGS)
    kwargs["datasource_class"] = datasource_class
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    print(f"\n{'='*65}")
    print(f"  {label}")
    print(f"{'='*65}")
    t0 = time.time()

    results, strategy = Momentum.run_backtest(**kwargs)
    elapsed = time.time() - t0

    # Extraction des métriques (QuantStats si disponible)
    pv = getattr(strategy, "portfolio_value", None)
    ret_total = (pv - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 if pv else None

    # Tentative d'extraction des stats QuantStats
    stats = {}
    if results is not None and hasattr(results, "__iter__"):
        try:
            stats = {k: v for k, v in results.items()}
        except Exception:
            pass

    summary = {
        "label": label,
        "portfolio_value_final": pv,
        "return_total_pct": ret_total,
        "elapsed_s": elapsed,
        "stats": stats,
    }
    return summary


# ── Affichage synthétique ──────────────────────────────────────────────────────
def print_summary(runs: list[dict], header: str) -> None:
    print(f"\n{'='*65}")
    print(f"  {header}")
    print(f"{'='*65}")
    for r in runs:
        pv = r["portfolio_value_final"]
        rt = r["return_total_pct"]
        pv_str = f"{pv:,.2f} USD" if pv is not None else "N/A"
        rt_str = f"{rt:+.2f}%" if rt is not None else "N/A"
        print(f"  [{r['label']}]  Valeur finale : {pv_str}  |  Rendement total : {rt_str}  |  Durée : {r['elapsed_s']:.1f}s")
    print()


# ── Programme principal ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Étape 2 — Validation Momentum LumiBot")
    parser.add_argument("--yahoo-only", action="store_true", help="Tester Yahoo uniquement")
    parser.add_argument("--alpaca-only", action="store_true", help="Tester Alpaca uniquement")
    parser.add_argument("--runs", type=int, default=2, help="Nombre d'exécutions par source (défaut: 2)")
    args = parser.parse_args()

    print("\n" + "="*65)
    print("  ÉTAPE 2 — VALIDATION STRATÉGIE MOMENTUM (ORIGINALE)")
    print(f"  Stratégie  : lumibot/example_strategies/stock_momentum.py")
    print(f"  Univers    : {DEFAULT_SYMBOLS}")
    print(f"  Période    : {BACKTEST_START.date()} → {BACKTEST_END.date()}")
    print(f"  Capital    : {INITIAL_CAPITAL:,} USD")
    print(f"  Benchmark  : {BENCHMARK}")
    print(f"  Exécutions : {args.runs} par source")
    print("="*65)

    all_results = []

    # ── TEST ALPACA ─────────────────────────────────────────────────────────
    if not args.yahoo_only:
        alpaca_extra = {
            "datasource_class": AlpacaBacktesting,
            "config": ALPACA_CONFIG,
            "full_window": True,
        }
        for run_n in range(1, args.runs + 1):
            label = f"Alpaca Run {run_n}"
            try:
                r = run_backtest(label, AlpacaBacktesting, alpaca_extra)
                all_results.append(r)
                print(f"  ✓ {label} terminé — valeur finale : {r['portfolio_value_final']:,.2f} USD")
            except Exception as exc:
                print(f"  ✗ {label} ÉCHOUÉ : {exc}")
                all_results.append({"label": label, "portfolio_value_final": None,
                                     "return_total_pct": None, "elapsed_s": 0, "stats": {}, "error": str(exc)})

    # ── TEST YAHOO ──────────────────────────────────────────────────────────
    if not args.alpaca_only:
        for run_n in range(1, args.runs + 1):
            label = f"Yahoo Run {run_n}"
            try:
                r = run_backtest(label, YahooDataBacktesting)
                all_results.append(r)
                print(f"  ✓ {label} terminé — valeur finale : {r['portfolio_value_final']:,.2f} USD")
            except Exception as exc:
                print(f"  ✗ {label} ÉCHOUÉ : {exc}")
                all_results.append({"label": label, "portfolio_value_final": None,
                                     "return_total_pct": None, "elapsed_s": 0, "stats": {}, "error": str(exc)})

    print_summary(all_results, "SYNTHÈSE DES RÉSULTATS — ÉTAPE 2 MOMENTUM")

    # Vérification de la reproductibilité
    alpaca_runs = [r for r in all_results if r["label"].startswith("Alpaca") and r["portfolio_value_final"] is not None]
    yahoo_runs = [r for r in all_results if r["label"].startswith("Yahoo") and r["portfolio_value_final"] is not None]

    if len(alpaca_runs) >= 2:
        vals = [r["portfolio_value_final"] for r in alpaca_runs]
        ok = all(abs(v - vals[0]) < 0.01 for v in vals)
        print(f"  Reproductibilité Alpaca  : {'✓ CONFORME' if ok else '✗ ÉCART DÉTECTÉ'}")

    if len(yahoo_runs) >= 2:
        vals = [r["portfolio_value_final"] for r in yahoo_runs]
        ok = all(abs(v - vals[0]) < 0.01 for v in vals)
        print(f"  Reproductibilité Yahoo   : {'✓ CONFORME' if ok else '✗ ÉCART DÉTECTÉ'}")

    print()
    return all_results


if __name__ == "__main__":
    main()

