"""Native lifecycle adapter checks without broker construction or model calls."""
from datetime import datetime
import importlib
import json
import os
from pathlib import Path
import socket
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mini_fund.common.contracts import Phase
from mini_fund.common.triggers import NY
from mini_fund.checks.test_triggers import plan


class NativeAdapterChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import dotenv
        with patch.dict(os.environ, {
            "IS_BACKTESTING": "True", "LUMIBOT_CONNECT_STREAM": "false",
            "LUMIBOT_START_ORDERS_THREAD": "false",
        }), patch.object(dotenv, "load_dotenv", return_value=False), patch.object(
            socket.socket, "connect", side_effect=AssertionError("Unexpected network access")
        ):
            cls.base = importlib.import_module("mini_fund.strategies.base").MiniFundStrategyBase

    def probe(self, day):
        base = self.base
        class LifecycleProbe(base):
            # Test-only object: never invokes Strategy.__init__ or any runner.
            @property
            def vars(self):
                return self.test_vars

            def initialize(self):
                pass

            def run_phase(self, phase):
                self.calls.append(phase)

            def get_datetime(self):
                return self.now

            def log_message(self, message, **kwargs):
                self.messages.append(message)

        obj = object.__new__(LifecycleProbe)
        obj.test_vars = SimpleNamespace()
        obj.broker = SimpleNamespace(market="NYSE")
        obj.calls, obj.messages = [], []
        obj.now = datetime.fromisoformat(day).replace(hour=9, minute=0, tzinfo=NY)
        config = {
            "timezone": "America/New_York", "phase_times": plan(),
            "triggers": {"poll_seconds": 1, "max_lateness_seconds": 5},
        }
        obj.configure_phase_triggers(config)
        return obj

    def test_native_calendar_and_all_lifecycle_hooks(self):
        obj = self.probe("2025-07-02")
        obj.before_market_opens()
        obj.before_market_opens()
        for hour, minute in [(9,45), (11,30)]:
            obj.now = obj.now.replace(hour=hour, minute=minute)
            obj.on_trading_iteration()
        obj.now = obj.now.replace(hour=15, minute=45)
        obj.before_market_closes()
        self.assertEqual(obj.calls, list(Phase))
        self.assertEqual(obj.minutes_before_opening, 30)
        self.assertEqual(obj.minutes_before_closing, 15)
        self.assertEqual(obj.sleeptime, "1S")

    def test_real_calendar_early_close_and_holiday(self):
        obj = self.probe("2025-07-03")
        obj.now = obj.now.replace(hour=12, minute=45)
        obj.before_market_closes()
        self.assertEqual(obj.calls, [Phase.BEFORE_CLOSE])
        obj.now = obj.now.replace(day=4, hour=9, minute=0)
        obj.before_market_opens()
        self.assertEqual(obj.calls, [Phase.BEFORE_CLOSE])

    def test_current_config_keeps_all_triggers_disabled(self):
        path = Path(__file__).resolve().parents[1] / "config/application.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(all(value is None for value in config["phase_times"].values()))
        self.assertIsNone(config["triggers"]["max_lateness_seconds"])

    def test_run_schedule_cannot_be_reconfigured_silently(self):
        obj = self.probe("2025-07-02")
        with self.assertRaises(RuntimeError):
            obj.configure_phase_triggers({})


if __name__ == "__main__":
    unittest.main()
