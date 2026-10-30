"""Future adapter to Strategy.run_live; no broker import or connection.

Before connecting: frozen release/configuration, account exclusivity, isolated
memory/state and reconciliation of positions and pending orders are required.
"""


def launch_live(*args, **kwargs):
    """No live launch is possible from this architecture shell."""
    raise NotImplementedError("Live launcher is not connected in the empty architecture.")
