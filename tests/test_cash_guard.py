"""Synthetic price fixtures exercise funding invariants; no vendor calls."""
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor

import pytest

from lumibot.backtesting import BacktestingBroker, PandasDataBacktesting
from lumibot.backtesting.cash_guard import CashGuard, CashGuardError
from lumibot.entities import Asset, Order, Position, TradingFee
from lumibot.strategies.strategy import Strategy


def order(quantity=5, side="buy", symbol="ALFA", **kwargs):
    return Order("NeutralGuard", Asset(symbol), quantity, side, **kwargs)


@pytest.mark.parametrize("config", [
    {"mode": "invalid"}, {"mode": "margin"},
    {"mode": "margin", "max_borrow": -1},
    {"mode": "margin", "max_borrow": float("nan")},
    {"mode": "cash", "max_borrow": 100},
    {"price_buffer_pct": -0.1}, {"price_buffer_pct": 2},
])
def test_invalid_config_fails_before_trading(config):
    with pytest.raises(ValueError):
        CashGuard(**config)


@pytest.mark.parametrize("mode,limit", [("cash", None), ("margin", 200)])
def test_exact_limit_is_allowed_but_one_cent_over_is_rejected(mode, limit):
    g = CashGuard(mode, max_borrow=limit, price_buffer_pct=0)
    o = order(12 if limit else 10)
    g.reserve(o, cash=1000, held=0, price=100, fee=0)
    g.check_fill(o, cash=1000, held=0, price=100, quantity=o.quantity, fee=0)
    with pytest.raises(CashGuardError, match="FILL_LIMIT_EXCEEDED"):
        g.check_fill(o, cash=1000, held=0, price=100, quantity=o.quantity, fee="0.01")


def test_queued_buys_cannot_spend_the_same_cash():
    g = CashGuard("cash", price_buffer_pct=0)
    g.reserve(order(6), cash=1000, held=0, price=100, fee=0)
    with pytest.raises(CashGuardError, match="INSUFFICIENT_FUNDS"):
        g.reserve(order(5, symbol="BETA"), cash=1000, held=0, price=100, fee=0)


def test_cancelled_reservation_is_released_but_cancelling_stays_reserved():
    g = CashGuard("cash", price_buffer_pct=0)
    a = order(8)
    g.reserve(a, cash=1000, held=0, price=100, fee=0)
    a.status = "cancelling"
    with pytest.raises(CashGuardError):
        g.reserve(order(3), cash=1000, held=0, price=100, fee=0)
    a.status = "canceled"
    g.reserve(order(10), cash=1000, held=0, price=100, fee=0)
    assert g.snapshot()["reserved_cash"] == "1000"


def test_failed_modify_keeps_the_old_reservation():
    g = CashGuard("cash", price_buffer_pct=0)
    a = order(5, limit_price=100)
    g.reserve(a, cash=1000, held=0, price=100, fee=0)
    with pytest.raises(CashGuardError):
        g.reserve(a, cash=1000, held=0, price=300, fee=0)
    assert g.snapshot()["reserved_cash"] == "500"


def test_sale_never_reserves_future_cash_and_cannot_duplicate_a_close():
    g = CashGuard("cash", price_buffer_pct=0)
    sell = order(5, "sell")
    g.reserve(sell, cash=0, held=5, price=100, fee=0)
    with pytest.raises(CashGuardError, match="INSUFFICIENT_FUNDS"):
        g.reserve(order(1), cash=0, held=5, price=100, fee=0)
    with pytest.raises(CashGuardError, match="INSUFFICIENT_POSITION"):
        g.reserve(order(1, "sell"), cash=0, held=5, price=100, fee=0)


def test_sell_can_reduce_existing_debt_without_going_short():
    g = CashGuard("cash")
    g.check_fill(order(1, "sell"), cash=-500, held=1, price=100, quantity=1, fee=0)
    with pytest.raises(CashGuardError, match="INSUFFICIENT_POSITION"):
        g.check_fill(order(2, "sell"), cash=-500, held=1, price=100, quantity=2, fee=0)


def test_pending_fill_ledger_avoids_reusing_cash_before_async_notification():
    g = CashGuard("cash", price_buffer_pct=0)
    a = order(8)
    g.record_fill(a, 8, 100)
    assert g.effective_cash(1000) == 200
    with pytest.raises(CashGuardError):
        g.reserve(order(3), cash=g.effective_cash(1000), held=0, price=100, fee=0)
    g.acknowledge_fill(a, 8, 100)
    assert g.effective_cash(200) == 200
    g.acknowledge_fill(a, 8, 100)  # Duplicate acknowledgement cannot manufacture credit.
    assert g.effective_cash(200) == 200


def test_partial_fill_reduces_reservation_without_releasing_the_remainder():
    g = CashGuard("cash", price_buffer_pct=0)
    a = order(10)
    g.reserve(a, cash=1000, held=0, price=100, fee=0)
    a.add_transaction(100, 4)
    a.status = "partial_fill"
    g.after_fill(a)
    # Decimal exponents are representation details, not funding behavior.
    assert Decimal(g.snapshot()["reserved_cash"]) == 600


def test_concurrent_reservations_admit_only_what_cash_can_fund():
    g = CashGuard("cash", price_buffer_pct=0)
    def admit(_):
        try:
            g.reserve(order(1), cash=100, held=0, price=100, fee=0)
            return True
        except CashGuardError:
            return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(admit, range(20))) == 1


@pytest.mark.parametrize("bad", [None, 0, -1, float("nan"), float("inf")])
def test_missing_or_invalid_prices_are_never_accepted(bad):
    with pytest.raises(CashGuardError):
        CashGuard("cash").reserve(order(), cash=1000, held=0, price=bad, fee=0)


class Passive(Strategy):
    def initialize(self):
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        pass


@pytest.fixture
def make_strategy(monkeypatch):
    made = []
    def make(mode="cash", max_borrow=None, fees=None, name="NeutralGuard"):
        source = PandasDataBacktesting(datetime_start=datetime(2025, 1, 2),
                                       datetime_end=datetime(2025, 1, 10))
        broker = BacktestingBroker(source)
        monkeypatch.setattr(source, "get_last_price", lambda *args, **kwargs: 100)
        cfg = {"mode": mode, "price_buffer_pct": 0}
        if max_borrow is not None:
            cfg["max_borrow"] = max_borrow
        s = Passive(broker=broker, budget=1000, name=name, risk_free_rate=0,
                    benchmark_asset=None, cash_guard=cfg, buy_trading_fees=fees or [])
        made.append(s)
        return s
    yield make
    for s in made:
        s.broker.stream.stop()


def submit(s, qty, side="buy", **kwargs):
    o = s.create_order("ALFA", qty, side, **kwargs)
    return s.broker.submit_order(o)


def drain(s):
    s._executor.process_queue(skip_first_iteration_events=False)


def test_real_broker_rejects_oversized_order_without_a_position(make_strategy):
    s = make_strategy()
    o = submit(s, 11)
    assert o.status == "error"
    assert s.cash == 1000
    assert s.broker.get_tracked_position(s.name, o.asset) is None
    assert s.broker.get_cash_guard_summary(s)["rejections"][-1]["code"] == "INSUFFICIENT_FUNDS"


@pytest.mark.parametrize("mode,limit,qty,expected_cash", [
    ("cash", None, 10, 0), ("margin", 200, 12, -200), ("disabled", None, 12, -200),
])
def test_real_fill_applies_all_three_modes(make_strategy, mode, limit, qty, expected_cash):
    s = make_strategy(mode, limit)
    o = submit(s, qty)
    s.broker._execute_filled_order(o, 100, Decimal(qty), s)
    drain(s)
    assert o.is_filled()
    assert s.cash == expected_cash


def test_gap_at_actual_fill_is_rejected_before_cash_or_positions_change(make_strategy):
    s = make_strategy()
    o = submit(s, 10)
    s.broker._execute_filled_order(o, 101, Decimal(10), s)
    drain(s)
    assert o.status == "error"
    assert s.cash == 1000
    assert s.broker.get_tracked_position(s.name, o.asset) is None


def test_real_batch_reservations_are_shared_and_cancel_releases_them(make_strategy):
    s = make_strategy()
    a, b = s.create_order("ALFA", 6, "buy"), s.create_order("BETA", 5, "buy")
    s.broker.submit_orders([a, b])
    assert a.status != "error" and b.status == "error"
    s.broker.cancel_order(a)
    c = submit(s, 10)
    assert c.status != "error"


def test_fees_count_at_submission(make_strategy):
    s = make_strategy(fees=[TradingFee(flat_fee=1)])
    o = submit(s, 10)
    assert o.status == "error"


def test_actual_fill_fees_cannot_overdraw_cash(make_strategy, monkeypatch):
    s = make_strategy()
    o = submit(s, 10)
    monkeypatch.setattr(s.broker, "calculate_trade_cost", lambda *a, **k: Decimal(1))
    s.broker._execute_filled_order(o, 100, Decimal(10), s)
    assert o.status == "error" and s.cash == 1000


def test_queued_cash_events_cannot_allow_two_fills_to_overdraw(make_strategy):
    s = make_strategy()
    a = submit(s, 6)
    b = submit(s, 4)
    s.broker._execute_filled_order(a, 100, Decimal(6), s)
    # Deliberately do NOT drain StrategyExecutor's fill queue between fills.
    s.broker._execute_filled_order(b, 101, Decimal(4), s)
    drain(s)
    assert a.is_filled() and b.status == "error"
    assert s.cash == 400


def test_config_can_change_only_after_orders_and_cash_events_finish(make_strategy):
    s = make_strategy()
    a = submit(s, 5)
    with pytest.raises(ValueError):
        s.configure_cash_guard("disabled")
    s.broker._execute_filled_order(a, 100, Decimal(5), s)
    with pytest.raises(ValueError):
        s.configure_cash_guard("disabled")
    drain(s)
    s.configure_cash_guard("disabled")
    assert s.broker.get_cash_guard_summary(s)["mode"] == "disabled"


def test_unsupported_assets_and_atomic_packages_fail_before_submission(make_strategy):
    s = make_strategy()
    o = s.create_order(Asset("ALFA", asset_type="crypto"), 1, "buy")
    s.broker.submit_order(o)
    assert o.status == "error"
    a, b = s.create_order("ALFA", 1, "buy"), s.create_order("BETA", 1, "sell")
    with pytest.raises(CashGuardError, match="UNSUPPORTED_ORDER"):
        s.broker.submit_orders([a, b], is_multileg=True)
    assert not a.transactions and not b.transactions


def test_settings_include_selected_mode_and_rejections(make_strategy, tmp_path):
    import json
    s = make_strategy("margin", 123)
    submit(s, 12)
    path = tmp_path / "settings.json"
    s.write_backtest_settings(str(path))
    result = json.loads(path.read_text())["cash_guard"]
    assert result["mode"] == "margin" and result["max_borrow"] == "123"
    assert result["rejected_count"] == 1


def test_real_partial_fills_keep_cash_and_reservations_consistent(make_strategy, monkeypatch):
    s = make_strategy()
    # The existing engine enables partial fills only for a data-source quantity model.
    monkeypatch.setattr(s.broker.data_source, "get_backtest_fill_quantity", lambda *args: 4, raising=False)
    a = submit(s, 10)
    s.broker._execute_filled_order(a, 100, Decimal(4), s)
    assert Decimal(s.broker.get_cash_guard_summary(s)["reserved_cash"]) == 600
    s.broker._execute_filled_order(a, 100, Decimal(6), s)
    drain(s)
    summary = s.broker.get_cash_guard_summary(s)
    assert s.cash == 0
    assert Decimal(summary["reserved_cash"]) == 0
    assert Decimal(summary["pending_cash_effect"]) == 0
    assert s.broker.get_tracked_position(s.name, a.asset).quantity == 10


def test_real_failed_modification_preserves_order_and_reserved_funds(make_strategy):
    s = make_strategy()
    a = submit(s, 5, limit_price=100)
    assert s.broker.modify_order(a, limit_price=300) is False
    assert a.limit_price == 100 and a.status != "error"
    assert Decimal(s.broker.get_cash_guard_summary(s)["reserved_cash"]) == 500
    assert submit(s, 6).status == "error"


def test_quote_currency_mismatch_fails_closed(make_strategy):
    s = make_strategy()
    a = Order(s.name, Asset("ALFA"), 1, "buy", quote=Asset("EUR", asset_type="forex"))
    s.broker.submit_order(a)
    assert a.status == "error"
    assert s.broker.get_cash_guard_summary(s)["rejections"][-1]["code"] == "CURRENCY_MISMATCH"


def test_two_strategy_budgets_and_modes_do_not_leak(make_strategy):
    a = make_strategy()
    b = Passive(broker=a.broker, budget=1000, name="SecondGuard", risk_free_rate=0,
                benchmark_asset=None,
                cash_guard={"mode": "margin", "max_borrow": 200, "price_buffer_pct": 0})
    first = submit(a, 11)
    second = submit(b, 12)
    a.broker._execute_filled_order(second, 100, Decimal(12), b)
    drain(b)
    assert first.status == "error" and second.is_filled()
    assert a.cash == 1000 and b.cash == -200
    assert a.broker.get_cash_guard_summary(a)["mode"] == "cash"
    assert a.broker.get_cash_guard_summary(b)["mode"] == "margin"


def test_live_mode_is_explicitly_unsupported():
    with pytest.raises(NotImplementedError):
        Strategy.configure_cash_guard(SimpleNamespace(is_backtesting=False), "cash")


def test_unregistered_order_cannot_bypass_an_active_guard(make_strategy):
    s = make_strategy()
    with pytest.raises(CashGuardError, match="UNREGISTERED_STRATEGY"):
        s.broker.submit_order(Order("Unregistered", Asset("ALFA"), 100, "buy"))


def test_fill_cannot_be_charged_to_a_different_budget(make_strategy):
    s = make_strategy()
    a = submit(s, 5)
    with pytest.raises(CashGuardError, match="STRATEGY_MISMATCH"):
        s.broker._execute_filled_order(a, 100, Decimal(5), SimpleNamespace(name="Other"))


def test_cancelled_order_cannot_be_filled_later(make_strategy):
    s = make_strategy()
    a = submit(s, 5)
    s.broker.cancel_order(a)
    s.broker._execute_filled_order(a, 100, Decimal(5), s)
    drain(s)
    assert not a.transactions and s.cash == 1000
