"""Read-only inspection of the empty architecture: python -m mini_fund."""
import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    config = json.loads((root / "config" / "application.json").read_text(encoding="utf-8"))
    from .strategies import STRATEGIES
    print(json.dumps({
        "status": "empty_architecture",
        "available_strategies": list(STRATEGIES),
        "active_live_strategy": config["active_live_strategy"],
        "timezone": config["timezone"],
        "phase_times": config["phase_times"],
        "triggers": config["triggers"],
        "universe_source": config["universe_source"],
        "execution_connected": False,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
