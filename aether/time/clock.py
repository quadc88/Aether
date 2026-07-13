from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import yaml


DEFAULT_TIMEZONE = "Asia/Kuala_Lumpur"


def load_time_config(path: str = "config/time.yaml") -> dict:
    config_path = Path(path)

    if not config_path.exists():
        return {"timezone": DEFAULT_TIMEZONE}

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return data


def get_timezone() -> str:
    config = load_time_config()
    return config.get("timezone", DEFAULT_TIMEZONE)


def now():
    timezone = ZoneInfo(get_timezone())
    return datetime.now(timezone)


def now_iso() -> str:
    return now().isoformat()


def now_display() -> str:
    config = load_time_config()
    fmt = config.get("datetime_format", "%Y-%m-%d %H:%M:%S")
    return now().strftime(fmt)


def time_state() -> dict:
    return {
        "timezone": get_timezone(),
        "now": now_display(),
        "iso": now_iso(),
    }