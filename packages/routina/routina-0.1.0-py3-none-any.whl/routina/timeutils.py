"""Time utilities for routina."""

import time
import datetime
from typing import Union, Dict, Any, Optional
from .exceptions import ScheduleError


def seconds_to_human_readable(seconds: float) -> str:
    """Convert seconds to human readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.1f} hours"
    else:
        return f"{seconds/86400:.1f} days"


def parse_time_string(time_str: str) -> datetime.time:
    """Parse time string in format HH:MM or HH:MM:SS."""
    try:
        if ":" not in time_str:
            raise ValueError("Time must contain ':'")
        
        parts = time_str.split(":")
        if len(parts) == 2:
            hour, minute = map(int, parts)
            return datetime.time(hour, minute)
        elif len(parts) == 3:
            hour, minute, second = map(int, parts)
            return datetime.time(hour, minute, second)
        else:
            raise ValueError("Invalid time format")
    except (ValueError, TypeError) as e:
        raise ScheduleError(f"Invalid time format '{time_str}': {e}")


def get_next_occurrence(target_time: datetime.time, from_time: Optional[datetime.datetime] = None) -> datetime.datetime:
    """Get the next occurrence of a specific time."""
    if from_time is None:
        from_time = datetime.datetime.now()
    
    target_datetime = datetime.datetime.combine(from_time.date(), target_time)
    
    if target_datetime <= from_time:
        target_datetime += datetime.timedelta(days=1)
    
    return target_datetime


def is_weekday(dt: datetime.datetime) -> bool:
    """Check if datetime is a weekday (Monday-Friday)."""
    return dt.weekday() < 5


def is_weekend(dt: datetime.datetime) -> bool:
    """Check if datetime is a weekend (Saturday-Sunday)."""
    return dt.weekday() >= 5


def matches_weekdays(dt: datetime.datetime, weekdays: list) -> bool:
    """Check if datetime matches any of the specified weekdays."""
    return dt.weekday() in weekdays


def parse_cron_expression(cron_expr: str) -> Dict[str, Any]:
    """Parse a simplified cron expression."""
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ScheduleError(f"Cron expression must have 5 parts, got {len(parts)}")
    
    minute, hour, day, month, weekday = parts
    
    return {
        "minute": _parse_cron_field(minute, 0, 59),
        "hour": _parse_cron_field(hour, 0, 23),
        "day": _parse_cron_field(day, 1, 31),
        "month": _parse_cron_field(month, 1, 12),
        "weekday": _parse_cron_field(weekday, 0, 6),
    }


def _parse_cron_field(field: str, min_val: int, max_val: int) -> Union[str, list, int]:
    """Parse a single cron field."""
    if field == "*":
        return "*"
    elif "/" in field:
        base, step = field.split("/")
        if base == "*":
            return list(range(min_val, max_val + 1, int(step)))
        else:
            start = int(base)
            return list(range(start, max_val + 1, int(step)))
    elif "," in field:
        return [int(x) for x in field.split(",")]
    elif "-" in field:
        start, end = map(int, field.split("-"))
        return list(range(start, end + 1))
    else:
        return int(field)


def matches_cron_schedule(dt: datetime.datetime, cron_config: Dict[str, Any]) -> bool:
    """Check if datetime matches cron schedule."""
    minute = dt.minute
    hour = dt.hour
    day = dt.day
    month = dt.month
    weekday = dt.weekday()
    
    # Convert Sunday=0 to Sunday=7 for cron compatibility
    if weekday == 6:  # Sunday in Python
        cron_weekday = 0
    else:
        cron_weekday = weekday + 1
    
    return (
        _matches_cron_value(minute, cron_config["minute"]) and
        _matches_cron_value(hour, cron_config["hour"]) and
        _matches_cron_value(day, cron_config["day"]) and
        _matches_cron_value(month, cron_config["month"]) and
        _matches_cron_value(cron_weekday, cron_config["weekday"])
    )


def _matches_cron_value(value: int, cron_value: Union[str, list, int]) -> bool:
    """Check if value matches cron field value."""
    if cron_value == "*":
        return True
    elif isinstance(cron_value, list):
        return value in cron_value
    elif isinstance(cron_value, int):
        return value == cron_value
    else:
        return False


UNIT_MULTIPLIERS = {
    "seconds": 1,
    "minutes": 60,
    "hours": 3600,
    "days": 86400,
    "weeks": 604800,
    "months": 2592000,  # Approximate 30 days
}


def get_interval_seconds(n: int, unit: str) -> int:
    """Get interval in seconds for given unit."""
    if unit not in UNIT_MULTIPLIERS:
        raise ScheduleError(f"Unknown time unit: {unit}")
    return n * UNIT_MULTIPLIERS[unit] 