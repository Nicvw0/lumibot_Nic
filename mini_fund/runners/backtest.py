"""Future adapter to LumiBot Strategy.run_backtest, in a separate process."""


def launch_backtest(*args, **kwargs):
    """Not connected: no strategy, data source or period has been chosen."""
    raise NotImplementedError("Backtest launcher is not connected in the empty architecture.")
