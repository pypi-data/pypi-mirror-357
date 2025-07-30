"""Decorators for scheduling functions in routina."""

import functools
import datetime
import time
import traceback
from typing import Callable, Any, Optional, List, Union
from .store import get_storage_backend
from .timeutils import (
    get_interval_seconds,
    parse_time_string,
    get_next_occurrence,
    is_weekday,
    is_weekend,
    matches_weekdays,
    parse_cron_expression,
    matches_cron_schedule,
)
from .exceptions import ScheduleError, ExecutionError, TimeoutError, RetryExhaustedError


class ScheduledFunction:
    """Wrapper for scheduled functions with metadata."""
    
    def __init__(self, func: Callable, schedule_type: str, schedule_config: dict):
        self.func = func
        self.schedule_type = schedule_type
        self.schedule_config = schedule_config
        self.name = func.__name__
        self.module = func.__module__
        self.retry_count = schedule_config.get('retry_count', 0)
        self.retry_delay = schedule_config.get('retry_delay', 60)
        self.timeout = schedule_config.get('timeout', None)
        
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        """Execute the function if it's due to run."""
        if self.should_run():
            return self._execute_with_error_handling(*args, **kwargs)
        return None
    
    def should_run(self) -> bool:
        """Check if the function should run based on its schedule."""
        storage = get_storage_backend()
        
        if self.schedule_type == "interval":
            interval_seconds = self.schedule_config["interval_seconds"]
            return storage.should_run(self.name, interval_seconds)
        
        elif self.schedule_type == "time":
            target_time = self.schedule_config["target_time"]
            last_run = storage.get_function_status(self.name).get("last_run")
            
            if last_run is None:
                return True
            
            last_run_dt = datetime.datetime.fromtimestamp(last_run)
            next_run = get_next_occurrence(target_time, last_run_dt)
            return datetime.datetime.now() >= next_run
        
        elif self.schedule_type == "weekdays":
            if not is_weekday(datetime.datetime.now()):
                return False
            return storage.should_run(self.name, 86400)  # Once per day
        
        elif self.schedule_type == "weekends":
            if not is_weekend(datetime.datetime.now()):
                return False
            return storage.should_run(self.name, 86400)  # Once per day
        
        elif self.schedule_type == "days":
            weekdays = self.schedule_config["weekdays"]
            if not matches_weekdays(datetime.datetime.now(), weekdays):
                return False
            return storage.should_run(self.name, 86400)  # Once per day
        
        elif self.schedule_type == "cron":
            cron_config = self.schedule_config["cron_config"]
            if not matches_cron_schedule(datetime.datetime.now(), cron_config):
                return False
            return storage.should_run(self.name, 60)  # Check every minute
        
        return False
    
    def _execute_with_error_handling(self, *args, **kwargs) -> Any:
        """Execute function with retry logic and error handling."""
        storage = get_storage_backend()
        last_error = None
        
        for attempt in range(self.retry_count + 1):
            try:
                if self.timeout:
                    result = self._execute_with_timeout(*args, **kwargs)
                else:
                    result = self.func(*args, **kwargs)
                
                storage.record_run(self.name, success=True)
                return result
                
            except Exception as e:
                last_error = str(e)
                error_details = f"Attempt {attempt + 1}/{self.retry_count + 1}: {e}"
                
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    storage.record_run(self.name, success=False, error=error_details)
                    if self.retry_count > 0:
                        raise RetryExhaustedError(f"Function {self.name} failed after {self.retry_count + 1} attempts. Last error: {last_error}")
                    else:
                        raise ExecutionError(f"Function {self.name} failed: {last_error}")
    
    def _execute_with_timeout(self, *args, **kwargs) -> Any:
        """Execute function with timeout (simplified implementation)."""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Function {self.name} timed out after {self.timeout} seconds")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.timeout)
        
        try:
            result = self.func(*args, **kwargs)
            signal.alarm(0)
            return result
        finally:
            signal.signal(signal.SIGALRM, old_handler)


# Registry to keep track of all scheduled functions
_scheduled_functions: List[ScheduledFunction] = []


def _register_scheduled_function(scheduled_func: ScheduledFunction) -> None:
    """Register a scheduled function."""
    global _scheduled_functions
    _scheduled_functions.append(scheduled_func)


def get_all_scheduled_functions() -> List[ScheduledFunction]:
    """Get all registered scheduled functions."""
    return _scheduled_functions.copy()


def every_n_seconds(n: int, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run every n seconds."""
    if n <= 0:
        raise ScheduleError("Interval must be positive")
    
    def decorator(func: Callable) -> ScheduledFunction:
        schedule_config = {
            "interval_seconds": n,
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "timeout": timeout,
        }
        scheduled_func = ScheduledFunction(func, "interval", schedule_config)
        _register_scheduled_function(scheduled_func)
        return scheduled_func
    
    return decorator


def every_n_minutes(n: int, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run every n minutes."""
    return every_n_seconds(n * 60, retry_count, retry_delay, timeout)


def every_n_hours(n: int, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run every n hours."""
    return every_n_seconds(n * 3600, retry_count, retry_delay, timeout)


def every_n_days(n: int, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run every n days."""
    return every_n_seconds(n * 86400, retry_count, retry_delay, timeout)


def every_n_weeks(n: int, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run every n weeks."""
    return every_n_seconds(n * 604800, retry_count, retry_delay, timeout)


def every_n_months(n: int, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run every n months (approximate)."""
    return every_n_seconds(n * 2592000, retry_count, retry_delay, timeout)


def at_time(time_str: str, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run at a specific time daily."""
    target_time = parse_time_string(time_str)
    
    def decorator(func: Callable) -> ScheduledFunction:
        schedule_config = {
            "target_time": target_time,
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "timeout": timeout,
        }
        scheduled_func = ScheduledFunction(func, "time", schedule_config)
        _register_scheduled_function(scheduled_func)
        return scheduled_func
    
    return decorator


def on_weekdays(retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run on weekdays (Monday-Friday)."""
    def decorator(func: Callable) -> ScheduledFunction:
        schedule_config = {
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "timeout": timeout,
        }
        scheduled_func = ScheduledFunction(func, "weekdays", schedule_config)
        _register_scheduled_function(scheduled_func)
        return scheduled_func
    
    return decorator


def on_weekends(retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run on weekends (Saturday-Sunday)."""
    def decorator(func: Callable) -> ScheduledFunction:
        schedule_config = {
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "timeout": timeout,
        }
        scheduled_func = ScheduledFunction(func, "weekends", schedule_config)
        _register_scheduled_function(scheduled_func)
        return scheduled_func
    
    return decorator


def on_days(weekdays: Union[List[int], List[str]], retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function to run on specific weekdays.
    
    Args:
        weekdays: List of weekday numbers (0=Monday, 6=Sunday) or names
    """
    if isinstance(weekdays[0], str):
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekdays = [day_names.index(day.lower()) for day in weekdays]
    
    def decorator(func: Callable) -> ScheduledFunction:
        schedule_config = {
            "weekdays": weekdays,
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "timeout": timeout,
        }
        scheduled_func = ScheduledFunction(func, "days", schedule_config)
        _register_scheduled_function(scheduled_func)
        return scheduled_func
    
    return decorator


def cron_schedule(cron_expr: str, retry_count: int = 0, retry_delay: int = 60, timeout: Optional[int] = None) -> Callable:
    """Schedule function using cron expression.
    
    Args:
        cron_expr: Cron expression in format "minute hour day month weekday"
    """
    cron_config = parse_cron_expression(cron_expr)
    
    def decorator(func: Callable) -> ScheduledFunction:
        schedule_config = {
            "cron_config": cron_config,
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "timeout": timeout,
        }
        scheduled_func = ScheduledFunction(func, "cron", schedule_config)
        _register_scheduled_function(scheduled_func)
        return scheduled_func
    
    return decorator 