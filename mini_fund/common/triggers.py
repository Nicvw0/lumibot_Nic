"""Dispatch due phases when LumiBot invokes a lifecycle hook.

This module owns no thread, sleep, cron, calendar or broker connection.
All datetimes come from the caller (the real or simulated LumiBot clock).
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
import threading
from zoneinfo import ZoneInfo

from .contracts import Phase

NY = ZoneInfo("America/New_York")
UTC = timezone.utc


def aware(value):
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("A timezone-aware datetime is required.")
    return value.astimezone(UTC)


@dataclass(frozen=True)
class Session:
    opens: datetime
    closes: datetime

    def __post_init__(self):
        opening, closing = aware(self.opens), aware(self.closes)
        if opening >= closing or opening.astimezone(NY).date() != closing.astimezone(NY).date():
            raise ValueError("Expected one US equity session on a single New York date.")

    @property
    def day(self):
        return self.opens.astimezone(NY).date().isoformat()


class PhaseTriggers:
    """Per-session state, backed by the supplied native self.vars dictionary.

    A claimed/failed phase is never retried automatically, including when a
    persisted running entry is restored. Actual durability belongs to the
    configured LumiBot state backend. This is not cross-process exclusion.
    """
    def __init__(self, phase_times, max_lateness_seconds, state):
        if set(phase_times) != {phase.value for phase in Phase}:
            raise ValueError("Exactly the four phase keys are required.")
        self.plan = {}
        for phase in Phase:
            spec = phase_times[phase.value]
            if spec is None:
                continue
            if not isinstance(spec, dict) or set(spec) != {"anchor", "offset_minutes"}:
                raise ValueError("Use null or {anchor, offset_minutes}.")
            offset = spec["offset_minutes"]
            if isinstance(offset, bool) or not isinstance(offset, (int, float)) or not math.isfinite(offset):
                raise ValueError("offset_minutes must be a finite number.")
            anchor = spec["anchor"]
            if anchor not in {"open", "close"}:
                raise ValueError("anchor must be open or close.")
            if phase == Phase.BEFORE_OPEN and (anchor != "open" or offset >= 0):
                raise ValueError("before_open must precede the opening.")
            if phase == Phase.BEFORE_CLOSE and (anchor != "close" or offset >= 0):
                raise ValueError("before_close must precede the closing.")
            self.plan[phase] = (anchor, offset)
        if self.plan and (
            isinstance(max_lateness_seconds, bool)
            or not isinstance(max_lateness_seconds, (int, float))
            or not math.isfinite(max_lateness_seconds)
            or max_lateness_seconds < 0
        ):
            raise ValueError("Choose max_lateness_seconds before enabling any phase.")
        self.tolerance = max_lateness_seconds
        self.state = state
        self.lock = threading.RLock()

    def target(self, phase, session):
        anchor, offset = self.plan[phase]
        origin = session.opens if anchor == "open" else session.closes
        return aware(origin) + timedelta(minutes=offset)

    def poll(self, clock, session_for, execute, emit):
        """Claim once, run synchronously, record outcome; no automatic retries.

        Late phases are marked missed. Intraday targets outside an early-close
        session are marked outside_session. Exceptions are recorded and reported
        without retrying partially completed work.
        """
        events = []
        with self.lock:
            for phase in Phase:
                if phase not in self.plan:
                    continue
                now = aware(clock())
                session = session_for(now)
                if session is None or now.astimezone(NY).date().isoformat() != session.day:
                    continue
                key = session.day + "/" + phase.value
                if key in self.state:
                    continue
                target = self.target(phase, session)
                opening, closing = aware(session.opens), aware(session.closes)
                outside = target.astimezone(NY).date().isoformat() != session.day
                if phase != Phase.BEFORE_OPEN:
                    outside = outside or not opening <= target < closing
                if outside:
                    status = "outside_session"
                elif now < target:
                    continue
                elif now > target + timedelta(seconds=self.tolerance) or (
                    phase == Phase.BEFORE_OPEN and now >= opening
                ) or (phase != Phase.BEFORE_OPEN and now >= closing):
                    status = "missed"
                else:
                    status = "running"
                entry = {
                    "session": session.day, "phase": phase.value,
                    "target_utc": target.isoformat(), "observed_utc": now.isoformat(),
                    "lateness_seconds": (now - target).total_seconds(),
                    "status": status,
                }
                # Claim before user work: a recursive poll or a restored claim
                # cannot repeat a phase that may have already produced effects.
                self.state[key] = entry
                if status == "running":
                    emit(dict(entry))
                    try:
                        execute(phase)
                    except Exception as error:
                        entry.update(status="failed", error_type=type(error).__name__)
                    else:
                        entry["status"] = "completed"
                    entry["finished_utc"] = aware(clock()).isoformat()
                emit(dict(entry))
                events.append(dict(entry))
        return events
