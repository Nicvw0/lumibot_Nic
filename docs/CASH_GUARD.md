# CASH_GUARD

Opt-in order funding protection shared by long-only equity backtests.

Last Updated: 2026-10-30
Status: Implementation candidate; no live-broker qualification
Audience: Maintainers and strategy authors

## Overview

`BacktestingBroker` owns the checks, not individual trading signals. The policy
is per strategy budget, shared by all of its orders and independent of its data
provider. It is opt-in, with the default `disabled` preserving existing fills.
This contract is not a live buying-power model or a universal portfolio-margin
engine. Live configuration raises `NotImplementedError` rather than suggesting
that an unsupported broker is protected.

## Modes and public configuration

Pass `cash_guard` as a named argument to `run_backtest` or the strategy constructor:

```python
cash_guard={"mode": "cash"}
cash_guard={"mode": "margin", "max_borrow": 2000}
cash_guard={"mode": "disabled"}
```

The margin ceiling is a finite, non-negative absolute cash debit in the quote
currency. It is mandatory for `margin`; no unlimited margin default is inferred.
It is not a leverage multiple, regulatory margin requirement or broker buying
power. An optional `price_buffer_pct` defaults to `0.01`, a 1% estimate buffer
for orders without a hard limit price. It must be between 0 and 1.

`self.configure_cash_guard(mode, max_borrow=None, price_buffer_pct=0.01)` changes
the policy only when tracked orders and unapplied cash notifications are clear.
Cancel or finish orders first. There is no environment variable or hidden mode.

## Admission, execution and lifecycle

- Submissions reserve cash for buys, including estimated fees. Existing buys
  cannot spend the same funds twice. Pending sales do not create cash credit.
- Sales reserve their shares; both enabled modes reject short sales and
  over-closes. Simple stock/ETF orders only are supported. Packages, brackets,
  options, futures, crypto and mismatched quote currencies fail closed when
  protection is enabled. Disabled mode leaves their legacy paths unchanged.
- Limit modifications replace reservations atomically. An unaffordable change
  leaves the old order and reservation intact.
- Actual fill checks use the price after the existing slippage model and actual
  fees, before cash, positions, child orders or fees are changed. An excessive
  gap rejects the order; quantities are never silently reduced.
- A partial fill preserves its remainder's reservation. Canceled, expired,
  rejected and filled orders release reservations. `cancelling` is not terminal.
- Fill cash notifications are asynchronous. A pending notional ledger prevents
  the same funds being reused until the corresponding strategy cash update is
  acknowledged. It is protected by a reentrant policy lock.
- A sale may reduce an existing excessive debit without fully curing it. It
  may not increase that debit through fees or create a short position.

The guard checks order-driven cash effects. Deposits, withdrawals, manually
mutated cash, corporate actions, financing accruals and external adjustments
retain their existing framework rules; this is not a general ledger constraint.
Existing financing configuration is separate. The margin ceiling is tested at
order admission and execution, not guaranteed against later interest accrual.
No settlement-day or currency-conversion model is added.

## Audit and compatibility

The selected policy and each rejection are logged. Settings JSON includes
`cash_guard`: mode, limit, estimate buffer, outstanding reservations, pending
cash effect, rejection count and structured reasons. `CASH_GUARD[...]` codes
distinguish insufficient funds, fill gaps, unsupported orders, currency mismatch,
over-selling, unknown budgets and invalid inputs. Rejected submissions use the
normal error-order event. Strategies must handle rejected orders and derive
holdings from confirmed fills, not merely from attempted submissions.

Tests cover all modes, boundary fees, invalid inputs, concurrent reservations,
pending fills, partial fills, cancellation, modifications, unknown ownership,
isolated strategy budgets and the real BacktestingBroker/StrategyExecutor path.
Disabled mode is the negative control. No live requests, paid inference or
fabricated vendor history are needed for the synthetic unit fixtures.

Qualification is restricted to the explicit configuration classes above. A
passing isolated test does not qualify live adapters or downstream deployments.
