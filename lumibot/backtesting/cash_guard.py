"""Opt-in long-only equity order funding checks for BacktestingBroker.

This is not a live buying-power or portfolio-margin model. All amounts are in
the strategy's quote currency; no FX conversion or pending sale credit is used.
"""
from decimal import Decimal, InvalidOperation
from threading import RLock


class CashGuardError(ValueError):
    """A funding rejection with a stable, reportable reason code."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"CASH_GUARD[{code}]: {message}")


def number(value, label, *, positive=False, nonnegative=False):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise CashGuardError("INVALID_INPUT", f"{label} must be finite") from None
    if not result.is_finite() or (positive and result <= 0) or (nonnegative and result < 0):
        raise CashGuardError("INVALID_INPUT", f"invalid {label}")
    return result


class CashGuard:
    MODES = {"disabled", "cash", "margin"}

    def __init__(self, mode="disabled", max_borrow=None, price_buffer_pct=0.01):
        if mode not in self.MODES:
            raise ValueError("cash_guard mode must be 'disabled', 'cash' or 'margin'")
        self.mode = mode
        self.max_borrow = number(max_borrow, "max_borrow", nonnegative=True) if max_borrow is not None else None
        if mode == "margin" and self.max_borrow is None:
            raise ValueError("margin mode requires an explicit max_borrow in quote currency")
        if mode != "margin" and self.max_borrow not in (None, Decimal(0)):
            raise ValueError("max_borrow is only valid in margin mode")
        self.price_buffer_pct = number(price_buffer_pct, "price_buffer_pct", nonnegative=True)
        if self.price_buffer_pct > 1:
            raise ValueError("price_buffer_pct must be between 0 and 1")
        self.lock = RLock()
        self.reservations = {}
        self.rejections = []
        # Fill notifications update Strategy cash asynchronously. Keep their
        # notional in a shadow ledger until that exact cash event is applied.
        self.pending_fills = []

    @property
    def enabled(self):
        return self.mode != "disabled"

    @property
    def floor(self):
        return -self.max_borrow if self.mode == "margin" else Decimal(0)

    def prune(self):
        for key, entry in list(self.reservations.items()):
            if not entry["order"].is_active():
                self.reservations.pop(key, None)

    def release(self, order):
        self.reservations.pop(id(order), None)

    def effective_cash(self, cash):
        return number(cash, "cash") + sum((v[1] for v in self.pending_fills), Decimal(0))

    def record_fill(self, order, quantity, price, multiplier=1):
        effect = number(quantity, "quantity") * number(price, "price") * number(multiplier, "multiplier")
        if str(order.side) == "buy":
            effect = -effect
        token = (id(order), effect)
        self.pending_fills.append(token)
        return token

    def acknowledge_fill(self, order, quantity, price, multiplier=1):
        effect = number(quantity, "quantity") * number(price, "price") * number(multiplier, "multiplier")
        if str(order.side) == "buy":
            effect = -effect
        token = (id(order), effect)
        if token in self.pending_fills:
            self.pending_fills.remove(token)

    def supported(self, order, quote):
        if not self.enabled:
            return
        if (order.asset.asset_type != "stock" or order.order_class not in (None, "", "simple")
                or bool(order.child_orders)
                or str(order.side) not in {"buy", "sell"}
                or number(order.asset.multiplier, "multiplier", positive=True) != 1):
            raise CashGuardError("UNSUPPORTED_ORDER", "active guard supports simple long-only stock/ETF orders")
        if order.quote is not None and order.quote != quote:
            raise CashGuardError("CURRENCY_MISMATCH", "order quote must match the strategy cash currency")

    def remaining(self, order):
        filled = sum((number(t.quantity, "filled quantity", nonnegative=True)
                      for t in order.transactions), Decimal(0))
        return max(Decimal(0), number(order.quantity, "quantity", positive=True) - filled)

    def _other_cash(self, order):
        self.prune()
        return sum((v["amount"] for k, v in self.reservations.items() if k != id(order)), Decimal(0))

    def _other_sells(self, order):
        self.prune()
        return sum((v["quantity"] for k, v in self.reservations.items()
                    if k != id(order) and v["order"].asset == order.asset
                    and str(v["order"].side) == "sell"), Decimal(0))

    def reserve(self, order, *, cash, held, price, fee):
        """Atomic admission; a failed replacement leaves its old reservation intact."""
        if not self.enabled:
            return
        with self.lock:
            quantity = self.remaining(order)
            price = number(price, "estimated price", positive=True)
            fee = number(fee, "estimated fee", nonnegative=True)
            cash = number(cash, "cash")
            amount = Decimal(0)
            if str(order.side) == "buy":
                # A limit is a hard price cap. Other order types need a gap buffer.
                buffer = Decimal(0) if str(order.order_type) in {"limit", "stop_limit"} else self.price_buffer_pct
                amount = quantity * price * (1 + buffer) + fee
                if cash - self._other_cash(order) - amount < self.floor:
                    raise CashGuardError("INSUFFICIENT_FUNDS", "cash minus existing reservations would exceed the borrowing limit")
            else:
                if quantity + self._other_sells(order) > number(held, "held quantity", nonnegative=True):
                    raise CashGuardError("INSUFFICIENT_POSITION", "sale would create a short position")
                # Do not credit the proceeds of this sale until it actually fills.
            self.reservations[id(order)] = {"order": order, "quantity": quantity, "amount": amount}

    def check_fill(self, order, *, cash, held, price, quantity, fee):
        """Recheck the actual (slippage-adjusted) fill price and actual fee."""
        if not self.enabled:
            return
        quantity = number(quantity, "fill quantity", positive=True)
        price = number(price, "fill price", positive=True)
        fee = number(fee, "fill fee", nonnegative=True)
        cash = number(cash, "cash")
        remaining = self.remaining(order)
        if quantity > remaining:
            raise CashGuardError("INVALID_INPUT", "fill exceeds remaining order quantity")
        if str(order.side) == "buy":
            own = self.reservations.get(id(order))
            future_reserve = own["amount"] * (remaining - quantity) / remaining if own else Decimal(0)
            projected = cash - quantity * price - fee - self._other_cash(order) - future_reserve
            if projected < self.floor:
                raise CashGuardError("FILL_LIMIT_EXCEEDED", "actual fill cost would consume reserved funds or exceed the borrowing limit")
        else:
            if quantity > number(held, "held quantity", nonnegative=True):
                raise CashGuardError("INSUFFICIENT_POSITION", "sale would create a short position")
            projected = cash + quantity * price - fee
            # Allow a sale to reduce an already excessive debit, but not worsen it.
            if projected < self.floor and projected < cash:
                raise CashGuardError("FILL_LIMIT_EXCEEDED", "sale fees would increase an excessive debit")

    def after_fill(self, order):
        entry = self.reservations.get(id(order))
        if entry is None:
            return
        remaining = self.remaining(order)
        if not order.is_active() or remaining == 0:
            self.release(order)
        else:
            entry["amount"] *= remaining / entry["quantity"]
            entry["quantity"] = remaining

    def snapshot(self):
        with self.lock:
            self.prune()
            return {"mode": self.mode, "max_borrow": str(self.max_borrow) if self.max_borrow is not None else None,
                    "price_buffer_pct": str(self.price_buffer_pct),
                    "reserved_cash": str(sum((v["amount"] for v in self.reservations.values()), Decimal(0))),
                    "pending_cash_effect": str(sum((v[1] for v in self.pending_fills), Decimal(0))),
                    "rejected_count": len(self.rejections), "rejections": list(self.rejections),
                    "scope": "backtest_simple_long_only_stocks_etfs"}
