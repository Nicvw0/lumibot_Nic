"""Abstract strategy with native LumiBot lifecycle phase triggers."""
from abc import ABC, abstractmethod
import json
from pathlib import Path
from datetime import timedelta

from lumibot.strategies import Strategy

from mini_fund.common.triggers import NY, PhaseTriggers, Session


class MiniFundStrategyBase(Strategy, ABC):
    """No concrete strategy, agents, universe or orders are defined.

    A future initialize() calls configure_phase_triggers() once. Intraday
    checking uses LumiBot's own loop; no application scheduler is created.
    """

    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    def configure_phase_triggers(self, config=None):
        if hasattr(self, "_phase_triggers"):
            raise RuntimeError("Triggers are frozen for this run; restart to change them.")
        if config is None:
            path = Path(__file__).resolve().parents[1] / "config" / "application.json"
            config = json.loads(path.read_text(encoding="utf-8"))
        if config.get("timezone") != "America/New_York":
            raise ValueError("The equity session timezone must be America/New_York.")
        settings = config["triggers"]
        poll = settings["poll_seconds"]
        if isinstance(poll, bool) or not isinstance(poll, int) or poll < 1:
            raise ValueError("poll_seconds must be a positive integer.")
        phases = config["phase_times"]
        # Native lifecycle hooks set the pre-open and pre-close wake windows.
        # Defaults in application.json do not select any business phase times.
        ledger = getattr(self.vars, "mini_fund_phase_runs", None)
        if ledger is None:
            ledger = {}
            self.vars.mini_fund_phase_runs = ledger
        self._phase_triggers = PhaseTriggers(phases, settings["max_lateness_seconds"], ledger)
        self._phase_session_cache = None
        self.sleeptime = str(poll) + "S"
        before = phases["before_open"]
        closing = phases["before_close"]
        if before is not None:
            self.minutes_before_opening = -before["offset_minutes"]
        if closing is not None:
            self.minutes_before_closing = -closing["offset_minutes"]

    def _session_for(self, instant):
        # Native calendar helper, bounded to the simulated/current local day:
        # weekends/holidays produce no session; early closes and DST are native.
        from lumibot.tools.helpers import get_trading_days

        day = instant.astimezone(NY).date()
        cached = self._phase_session_cache
        if cached is not None and cached[0] == day:
            return cached[1]
        schedule = get_trading_days(
            market=self.broker.market,
            start_date=day.isoformat(),
            end_date=(day + timedelta(days=1)).isoformat(),
        )
        session = None
        for _, row in schedule.iterrows():
            opening, closing = row["market_open"], row["market_close"]
            if opening.astimezone(NY).date() == day:
                session = Session(opening, closing)
                break
        self._phase_session_cache = (day, session)
        return session

    def _poll_phases(self):
        if not hasattr(self, "_phase_triggers"):
            raise RuntimeError("Call configure_phase_triggers() from initialize() first.")
        return self._phase_triggers.poll(
            self.get_datetime, self._session_for, self.run_phase,
            lambda event: self.log_message("MINI_FUND_PHASE " + json.dumps(event)),
        )

    def before_market_opens(self):
        self._poll_phases()

    def before_starting_trading(self):
        self._poll_phases()

    def on_trading_iteration(self):
        self._poll_phases()

    def before_market_closes(self):
        self._poll_phases()

    def after_market_closes(self):
        # Record any missed remaining moments; never execute business work
        # after its admissible session window.
        self._poll_phases()

    @abstractmethod
    def run_phase(self, phase):
        """Future delegation to phase modules; there are no business tasks yet."""
        raise NotImplementedError
