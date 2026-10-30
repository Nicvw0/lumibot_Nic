"""Reserved business phase: après ouverture. No task is implemented."""
from mini_fund.common.contracts import PhaseContext


def run(context: PhaseContext):
    raise NotImplementedError("Phase after_open is not implemented.")
