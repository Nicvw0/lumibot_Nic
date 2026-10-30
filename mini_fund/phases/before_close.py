"""Reserved business phase: avant clôture. No task is implemented."""
from mini_fund.common.contracts import PhaseContext


def run(context: PhaseContext):
    raise NotImplementedError("Phase before_close is not implemented.")
