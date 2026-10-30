"""Reserved business phase: avant séance. No task is implemented."""
from mini_fund.common.contracts import PhaseContext


def run(context: PhaseContext):
    raise NotImplementedError("Phase before_open is not implemented.")
