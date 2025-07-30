"""
routina: A Python-native, time-aware function runner — like cron, but all in code.

Example:
    from routina import every_n_days, run_if_due
    
    @every_n_days(2)
    def restart_server():
        print("🔁 Restarting server")
    
    if __name__ == "__main__":
        run_if_due(restart_server)
"""

from .decorators import (
    every_n_seconds,
    every_n_minutes,
    every_n_hours,
    every_n_days,
    every_n_weeks,
    every_n_months,
    at_time,
    on_weekdays,
    on_weekends,
    on_days,
    cron_schedule,
)
from .runner import (
    run_if_due,
    run_all_due,
    get_all_scheduled_functions,
    get_function_status,
    reset_function_history,
    print_status_report,
)
from .store import (
    set_storage_backend,
    get_storage_backend,
    clear_all_history,
    JSONStorage,
    SQLiteStorage,
    InMemoryStorage,
)
from .exceptions import (
    RoutinaError,
    StorageError,
    ScheduleError,
    ExecutionError,
)

__version__ = "0.1.0"
__author__ = "Andrew Wade"
__email__ = "andrew@example.com"

__all__ = [
    # Decorators
    "every_n_seconds",
    "every_n_minutes", 
    "every_n_hours",
    "every_n_days",
    "every_n_weeks",
    "every_n_months",
    "at_time",
    "on_weekdays",
    "on_weekends",
    "on_days",
    "cron_schedule",
    # Runner functions
    "run_if_due",
    "run_all_due",
    "get_all_scheduled_functions",
    "get_function_status",
    "reset_function_history",
    "print_status_report",
    # Storage
    "set_storage_backend",
    "get_storage_backend", 
    "clear_all_history",
    "JSONStorage",
    "SQLiteStorage",
    "InMemoryStorage",
    # Exceptions
    "RoutinaError",
    "StorageError",
    "ScheduleError",
    "ExecutionError",
] 