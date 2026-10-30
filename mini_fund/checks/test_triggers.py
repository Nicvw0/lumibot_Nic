"""Offline trigger tests. All business hours below are fixtures, not settings."""
from datetime import datetime, timedelta
import unittest
from zoneinfo import ZoneInfo

from mini_fund.common.contracts import Phase
from mini_fund.common.triggers import PhaseTriggers, Session

NY = ZoneInfo("America/New_York")


def dt(day="2025-07-02", hour=9, minute=30):
    return datetime.fromisoformat(day).replace(hour=hour, minute=minute, tzinfo=NY)


def plan():
    return {
        "before_open": {"anchor": "open", "offset_minutes": -30},
        "after_open": {"anchor": "open", "offset_minutes": 15},
        "mid_session": {"anchor": "open", "offset_minutes": 120},
        "before_close": {"anchor": "close", "offset_minutes": -15},
    }


class TriggerChecks(unittest.TestCase):
    def setUp(self):
        self.state, self.calls, self.events = {}, [], []
        self.engine = PhaseTriggers(plan(), 5, self.state)
        self.session = Session(dt(), dt(hour=16, minute=0))
        self.now = dt(hour=8)

    def poll(self, execute=None, session=True):
        return self.engine.poll(
            lambda: self.now, lambda _: self.session if session else None,
            execute or self.calls.append, self.events.append,
        )

    def test_not_before_time_and_exact_target_only_once(self):
        self.poll()
        self.assertEqual(self.calls, [])
        for _ in range(3):
            self.now = dt(hour=9, minute=0)
            self.poll()
        self.assertEqual(self.calls, [Phase.BEFORE_OPEN])
        self.assertEqual(self.state["2025-07-02/before_open"]["status"], "completed")

    def test_all_four_and_repeat_poll(self):
        for hour, minute in [(9, 0), (9, 45), (11, 30), (15, 45)]:
            self.now = dt(hour=hour, minute=minute)
            self.poll()
            self.poll()
        self.assertEqual(self.calls, list(Phase))

    def test_small_delay_allowed_and_lateness_recorded(self):
        self.now = dt(hour=9, minute=0) + timedelta(seconds=3)
        self.poll()
        self.assertEqual(self.calls, [Phase.BEFORE_OPEN])
        self.assertEqual(self.state["2025-07-02/before_open"]["lateness_seconds"], 3)

    def test_late_start_skips_old_phase(self):
        self.now = dt(hour=9, minute=1)
        self.poll()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.state["2025-07-02/before_open"]["status"], "missed")

    def test_early_close_target_follows_closing(self):
        self.session = Session(dt(), dt(hour=13, minute=0))
        self.now = dt(hour=12, minute=45)
        self.poll()
        self.assertEqual(self.calls, [Phase.BEFORE_CLOSE])

    def test_intraday_target_outside_short_session_is_not_run(self):
        custom = plan()
        custom["mid_session"]["offset_minutes"] = 300
        self.engine = PhaseTriggers(custom, 5, self.state)
        self.session = Session(dt(), dt(hour=13, minute=0))
        self.now = dt(hour=9, minute=0)
        self.poll()
        self.assertEqual(self.state["2025-07-02/mid_session"]["status"], "outside_session")
        self.assertNotIn(Phase.MID_SESSION, self.calls)

    def test_holiday_no_session(self):
        self.poll(session=False)
        self.assertEqual(self.state, {})

    def test_failure_not_retried(self):
        def fail(phase):
            self.calls.append(phase)
            raise RuntimeError("test")
        self.now = dt(hour=9, minute=0)
        self.poll(fail)
        self.poll(fail)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.state["2025-07-02/before_open"]["status"], "failed")

    def test_restored_running_claim_not_repeated(self):
        self.state["2025-07-02/before_open"] = {"status": "running"}
        self.now = dt(hour=9, minute=0)
        self.poll()
        self.assertEqual(self.calls, [])

    def test_recursive_poll_does_not_repeat_phase(self):
        def recurse(phase):
            self.calls.append(phase)
            self.poll()
        self.now = dt(hour=9, minute=0)
        self.poll(recurse)
        self.assertEqual(self.calls, [Phase.BEFORE_OPEN])

    def test_next_day_is_independent(self):
        self.now = dt(hour=9, minute=0)
        self.poll()
        self.session = Session(dt("2025-07-03"), dt("2025-07-03", 13))
        self.now = dt("2025-07-03", 9, 0)
        self.poll()
        self.assertEqual(self.calls, [Phase.BEFORE_OPEN, Phase.BEFORE_OPEN])

    def test_callback_duration_rechecks_clock(self):
        self.now = dt(hour=9, minute=0)
        def advance(phase):
            self.calls.append(phase)
            self.now = dt(hour=10)
        self.poll(advance)
        self.assertEqual(self.calls, [Phase.BEFORE_OPEN])
        self.assertEqual(self.state["2025-07-02/after_open"]["status"], "missed")

    def test_no_phase_after_close_even_with_large_tolerance(self):
        self.engine = PhaseTriggers(plan(), 86400, self.state)
        self.now = dt(hour=17)
        self.poll()
        self.assertEqual(self.calls, [])

    def test_disabled_schedule_requires_no_tolerance(self):
        engine = PhaseTriggers({p.value: None for p in Phase}, None, {})
        self.assertEqual(engine.poll(lambda: self.now, lambda _: self.session, self.calls.append, self.events.append), [])

    def test_enabled_schedule_needs_explicit_tolerance(self):
        with self.assertRaises(ValueError):
            PhaseTriggers(plan(), None, {})

    def test_naive_datetime_rejected(self):
        self.now = datetime(2025, 7, 2, 9)
        with self.assertRaises(ValueError):
            self.poll()

    def test_dst_utc_target_changes_with_new_york(self):
        engine = PhaseTriggers(plan(), 5, {})
        winter = Session(dt("2025-01-06"), dt("2025-01-06", 16))
        summer = Session(dt("2025-07-02"), dt("2025-07-02", 16))
        self.assertEqual(engine.target(Phase.BEFORE_OPEN, winter).hour, 14)
        self.assertEqual(engine.target(Phase.BEFORE_OPEN, summer).hour, 13)


if __name__ == "__main__":
    unittest.main()
