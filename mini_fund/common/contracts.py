"""Names and boundaries only; no financial rule or runtime state."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class Phase(str, Enum):
    BEFORE_OPEN = "before_open"
    AFTER_OPEN = "after_open"
    MID_SESSION = "mid_session"
    BEFORE_CLOSE = "before_close"


@dataclass(frozen=True)
class PhaseContext:
    """Provided by a future dispatcher using LumiBot's clock and account state.

    None means that admissibility has not been computed, not that a supplied
    universe has passed its checks.
    """
    phase: Phase
    as_of: datetime
    strategy: Any
    eligible_symbols: tuple[str, ...] | None = None
