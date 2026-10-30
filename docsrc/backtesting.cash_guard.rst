Cash guard for equity backtests
==============================

The optional cash guard checks funding for simple, long-only stock and ETF
orders in ``BacktestingBroker``, regardless of the strategy or data provider.
It does not currently support paper/live brokers, derivatives, crypto,
brackets or atomic packages. Unsupported orders are rejected when enabled.

Select a mode
-------------

Pass one of these configurations as the named ``cash_guard`` argument to
``run_backtest`` or the strategy constructor:

.. code-block:: python

   cash_guard={"mode": "cash"}                       # No borrowing
   cash_guard={"mode": "margin", "max_borrow": 2000} # At most 2,000 quote units
   cash_guard={"mode": "disabled"}                   # Existing behavior

The default is ``disabled`` for backwards compatibility. ``margin`` requires
an explicit finite, non-negative ``max_borrow``. This is an absolute cash-debit
limit, not a leverage ratio or a model of your broker's margin requirements.

You can also configure it in ``initialize()``:

.. code-block:: python

   self.configure_cash_guard("cash")

To change modes later, all orders and pending cash notifications must be clear.

How orders are checked
----------------------

Buys reserve cash including estimated fees. Pending sales do not count as
available cash. Sells reserve shares and cannot create short positions. Orders
without a hard limit price use a configurable estimate buffer:
``price_buffer_pct=0.01`` means 1%, not 0.01%.

The guard checks again at the actual fill price, including slippage and fees.
A gap that makes an order unaffordable produces an error-order event. It does
not silently reduce the quantity. Strategies should handle rejections and
update their holdings from confirmed fills. A strategy that assumes every
submitted order succeeds may need separate changes.

Partial fills keep the remaining reservation. Cancellations, rejections and
completed orders release it; an unconfirmed cancellation does not. Limit-price
modifications must fit the funding limit before replacing a reservation.

Limits and reporting
--------------------

The selected mode and structured rejection reasons appear in logs and the
settings JSON under ``cash_guard``. The report includes the borrowing ceiling,
reserved cash, pending cash effect and rejection count.

This protects order funding, not every possible ledger change. Interest,
withdrawals, manual adjustments, corporate actions and settlement rules retain
their existing behavior. Financing costs are configured separately and can
change cash after a trade. No live buying-power or portfolio-margin model is
implied. Requests to enable the guard for live trading fail explicitly.
