"""Runner functions for executing scheduled tasks."""

import logging
from typing import Any, List, Optional, Dict
from .decorators import ScheduledFunction, get_all_scheduled_functions
from .store import get_storage_backend
from .timeutils import seconds_to_human_readable
from .exceptions import ExecutionError


def run_if_due(func: ScheduledFunction, *args, **kwargs) -> Any:
    """Run a scheduled function if it's due."""
    if not isinstance(func, ScheduledFunction):
        raise ExecutionError(f"Function {func} is not a scheduled function")
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error running scheduled function {func.name}: {e}")
        raise


def run_all_due(*args, **kwargs) -> Dict[str, Any]:
    """Run all scheduled functions that are due."""
    scheduled_functions = get_all_scheduled_functions()
    results = {}
    
    for func in scheduled_functions:
        try:
            result = func(*args, **kwargs)
            if result is not None:
                results[func.name] = {"success": True, "result": result}
        except Exception as e:
            results[func.name] = {"success": False, "error": str(e)}
            logging.error(f"Error running scheduled function {func.name}: {e}")
    
    return results


def get_function_status(func_name: str) -> Dict[str, Any]:
    """Get detailed status information for a function."""
    storage = get_storage_backend()
    status = storage.get_function_status(func_name)
    
    if not status.get("exists"):
        return {"exists": False, "message": f"Function '{func_name}' not found"}
    
    # Find the scheduled function for additional metadata
    scheduled_func = None
    for func in get_all_scheduled_functions():
        if func.name == func_name:
            scheduled_func = func
            break
    
    # Calculate human-readable time information
    result = {
        "exists": True,
        "name": func_name,
        "run_count": status.get("run_count", 0),
        "success_count": status.get("success_count", 0),
        "error_count": status.get("error_count", 0),
        "success_rate": 0.0,
    }
    
    if result["run_count"] > 0:
        result["success_rate"] = result["success_count"] / result["run_count"]
    
    # Add time information
    if status.get("first_run"):
        result["first_run"] = status["first_run"]
        result["first_run_human"] = seconds_to_human_readable(
            time.time() - status["first_run"]
        ) + " ago"
    
    if status.get("last_run"):
        result["last_run"] = status["last_run"]
        result["last_run_human"] = seconds_to_human_readable(
            time.time() - status["last_run"]
        ) + " ago"
    
    if status.get("last_error"):
        result["last_error"] = status["last_error"]
        if status.get("last_error_time"):
            result["last_error_time"] = status["last_error_time"]
            result["last_error_human"] = seconds_to_human_readable(
                time.time() - status["last_error_time"]
            ) + " ago"
    
    # Add schedule information if available
    if scheduled_func:
        result["schedule_type"] = scheduled_func.schedule_type
        result["schedule_config"] = scheduled_func.schedule_config
        result["module"] = scheduled_func.module
        result["retry_count"] = scheduled_func.retry_count
        result["retry_delay"] = scheduled_func.retry_delay
        result["timeout"] = scheduled_func.timeout
        
        # Calculate next run time for interval-based schedules
        if scheduled_func.schedule_type == "interval" and status.get("last_run"):
            interval_seconds = scheduled_func.schedule_config["interval_seconds"]
            next_run_timestamp = status["last_run"] + interval_seconds
            time_until_next = next_run_timestamp - time.time()
            
            if time_until_next > 0:
                result["next_run"] = next_run_timestamp
                result["next_run_human"] = "in " + seconds_to_human_readable(time_until_next)
            else:
                result["next_run_human"] = "now (overdue)"
    
    return result


def get_all_scheduled_functions_status() -> List[Dict[str, Any]]:
    """Get status for all scheduled functions."""
    scheduled_functions = get_all_scheduled_functions()
    return [get_function_status(func.name) for func in scheduled_functions]


def reset_function_history(func_name: str) -> bool:
    """Reset the execution history for a function."""
    storage = get_storage_backend()
    
    # Check if function exists
    if not storage.get_function_status(func_name).get("exists"):
        return False
    
    storage.reset_function(func_name)
    return True


def force_run(func_name: str, *args, **kwargs) -> Any:
    """Force run a scheduled function regardless of schedule."""
    scheduled_functions = get_all_scheduled_functions()
    
    for func in scheduled_functions:
        if func.name == func_name:
            # Temporarily bypass the schedule check
            original_should_run = func.should_run
            func.should_run = lambda: True
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                func.should_run = original_should_run
    
    raise ExecutionError(f"Scheduled function '{func_name}' not found")


def list_scheduled_functions() -> List[Dict[str, Any]]:
    """List all scheduled functions with their basic information."""
    scheduled_functions = get_all_scheduled_functions()
    
    return [
        {
            "name": func.name,
            "module": func.module,
            "schedule_type": func.schedule_type,
            "schedule_config": func.schedule_config,
            "retry_count": func.retry_count,
            "timeout": func.timeout,
        }
        for func in scheduled_functions
    ]


def print_status_report() -> None:
    """Print a comprehensive status report of all scheduled functions."""
    scheduled_functions = get_all_scheduled_functions()
    
    if not scheduled_functions:
        print("No scheduled functions found.")
        return
    
    print("=" * 80)
    print("ROUTINA STATUS REPORT")
    print("=" * 80)
    print(f"Total scheduled functions: {len(scheduled_functions)}")
    print()
    
    for func in scheduled_functions:
        status = get_function_status(func.name)
        print(f"📋 {func.name}")
        print(f"   Module: {func.module}")
        print(f"   Schedule: {func.schedule_type}")
        
        if status.get("run_count", 0) > 0:
            print(f"   Runs: {status['run_count']} (✅ {status['success_count']}, ❌ {status['error_count']})")
            print(f"   Success Rate: {status['success_rate']:.1%}")
            
            if status.get("last_run_human"):
                print(f"   Last Run: {status['last_run_human']}")
            
            if status.get("next_run_human"):
                print(f"   Next Run: {status['next_run_human']}")
            
            if status.get("last_error"):
                print(f"   Last Error: {status['last_error']}")
        else:
            print("   Status: Never run")
        
        print()


import time 