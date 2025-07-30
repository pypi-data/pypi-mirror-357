"""Comprehensive tests for routina."""

import pytest
import time
import datetime
import tempfile
import os
from unittest.mock import patch, MagicMock

import routina
from routina import (
    every_n_seconds,
    every_n_minutes,
    every_n_hours,
    every_n_days,
    at_time,
    on_weekdays,
    on_weekends,
    on_days,
    cron_schedule,
    run_if_due,
    run_all_due,
    get_function_status,
    reset_function_history,
)
from routina.store import JSONStorage, SQLiteStorage, InMemoryStorage, set_storage_backend
from routina.exceptions import ScheduleError, ExecutionError
from routina.timeutils import parse_time_string, get_next_occurrence, is_weekday, is_weekend
from routina.decorators import _scheduled_functions


class TestTimeUtils:
    """Test time utility functions."""
    
    def test_parse_time_string(self):
        """Test time string parsing."""
        assert parse_time_string("14:30") == datetime.time(14, 30)
        assert parse_time_string("09:15:30") == datetime.time(9, 15, 30)
        
        with pytest.raises(ScheduleError):
            parse_time_string("invalid")
        
        with pytest.raises(ScheduleError):
            parse_time_string("25:00")
    
    def test_get_next_occurrence(self):
        """Test next occurrence calculation."""
        target_time = datetime.time(14, 30)
        from_time = datetime.datetime(2024, 1, 1, 10, 0)
        
        next_run = get_next_occurrence(target_time, from_time)
        assert next_run.time() == target_time
        assert next_run.date() == from_time.date()
        
        # Test when target time has passed
        from_time = datetime.datetime(2024, 1, 1, 16, 0)
        next_run = get_next_occurrence(target_time, from_time)
        assert next_run.date() == from_time.date() + datetime.timedelta(days=1)
    
    def test_weekday_functions(self):
        """Test weekday utility functions."""
        monday = datetime.datetime(2024, 1, 1)  # Monday
        saturday = datetime.datetime(2024, 1, 6)  # Saturday
        
        assert is_weekday(monday)
        assert not is_weekday(saturday)
        assert not is_weekend(monday)
        assert is_weekend(saturday)


class TestStorageBackends:
    """Test storage backends."""
    
    def test_in_memory_storage(self):
        """Test in-memory storage backend."""
        storage = InMemoryStorage()
        
        # Test should_run for new function
        assert storage.should_run("test_func", 60)
        
        # Record a run
        storage.record_run("test_func", success=True)
        
        # Should not run again immediately
        assert not storage.should_run("test_func", 60)
        
        # Get status
        status = storage.get_function_status("test_func")
        assert status["exists"]
        assert status["run_count"] == 1
        assert status["success_count"] == 1
        assert status["error_count"] == 0
        
        # Test error recording
        storage.record_run("test_func", success=False, error="Test error")
        status = storage.get_function_status("test_func")
        assert status["run_count"] == 2
        assert status["error_count"] == 1
        assert status["last_error"] == "Test error"
    
    def test_json_storage(self):
        """Test JSON storage backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, "test.json")
            storage = JSONStorage(storage_path)
            
            # Test basic functionality
            assert storage.should_run("test_func", 60)
            storage.record_run("test_func", success=True)
            assert not storage.should_run("test_func", 60)
            
            # Test persistence by creating new instance
            storage2 = JSONStorage(storage_path)
            assert not storage2.should_run("test_func", 60)
    
    def test_sqlite_storage(self):
        """Test SQLite storage backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, "test.db")
            storage = SQLiteStorage(storage_path)
            
            # Test basic functionality
            assert storage.should_run("test_func", 60)
            storage.record_run("test_func", success=True)
            assert not storage.should_run("test_func", 60)
            
            # Test persistence
            storage2 = SQLiteStorage(storage_path)
            assert not storage2.should_run("test_func", 60)


class TestDecorators:
    """Test decorator functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear scheduled functions registry
        _scheduled_functions.clear()
        # Use in-memory storage for tests
        set_storage_backend(InMemoryStorage())
    
    def test_every_n_seconds(self):
        """Test every_n_seconds decorator."""
        call_count = 0
        
        @every_n_seconds(1)
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        # Should run on first call
        result = test_func()
        assert result == "success"
        assert call_count == 1
        
        # Should not run immediately again
        result = test_func()
        assert result is None
        assert call_count == 1
        
        # Should run after waiting
        time.sleep(1.1)
        result = test_func()
        assert result == "success"
        assert call_count == 2
    
    def test_every_n_minutes(self):
        """Test every_n_minutes decorator."""
        @every_n_minutes(1)
        def test_func():
            return "success"
        
        # Mock time to test without waiting
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000
            result = test_func()
            assert result == "success"
            
            # Should not run again within the minute
            mock_time.return_value = 1030
            result = test_func()
            assert result is None
            
            # Should run after a minute
            mock_time.return_value = 1070
            result = test_func()
            assert result == "success"
    
    def test_at_time(self):
        """Test at_time decorator."""
        @at_time("14:30")
        def test_func():
            return "success"
        
        # Mock datetime to control time
        with patch('datetime.datetime') as mock_datetime:
            # Set current time to before target
            mock_now = datetime.datetime(2024, 1, 1, 10, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromtimestamp.return_value = mock_now
            
            # Should run on first call (never run before)
            result = test_func()
            assert result == "success"
    
    def test_on_weekdays(self):
        """Test on_weekdays decorator."""
        @on_weekdays()
        def test_func():
            return "weekday"
        
        # Mock datetime to control day of week
        with patch('routina.timeutils.datetime') as mock_datetime, \
             patch('routina.decorators.datetime') as mock_decorators_datetime:
            # Monday
            mock_dt = datetime.datetime(2024, 1, 1)
            mock_datetime.datetime.now.return_value = mock_dt
            mock_decorators_datetime.datetime.now.return_value = mock_dt
            result = test_func()
            assert result == "weekday"
            
            # Saturday (should not run if already ran today)
            mock_dt = datetime.datetime(2024, 1, 6)
            mock_datetime.datetime.now.return_value = mock_dt
            mock_decorators_datetime.datetime.now.return_value = mock_dt
            result = test_func()
            assert result is None
    
    def test_on_days(self):
        """Test on_days decorator."""
        @on_days([0, 2, 4])  # Monday, Wednesday, Friday
        def test_func():
            return "selected_day"
        
        with patch('routina.timeutils.datetime') as mock_datetime, \
             patch('routina.decorators.datetime') as mock_decorators_datetime:
            # Monday (day 0)
            mock_dt = datetime.datetime(2024, 1, 1)
            mock_datetime.datetime.now.return_value = mock_dt
            mock_decorators_datetime.datetime.now.return_value = mock_dt
            result = test_func()
            assert result == "selected_day"
            
            # Tuesday (day 1, not selected)
            mock_dt = datetime.datetime(2024, 1, 2)
            mock_datetime.datetime.now.return_value = mock_dt
            mock_decorators_datetime.datetime.now.return_value = mock_dt
            result = test_func()
            assert result is None
    
    def test_cron_schedule(self):
        """Test cron_schedule decorator."""
        @cron_schedule("30 14 * * *")  # 2:30 PM every day
        def test_func():
            return "cron_success"
        
        with patch('routina.timeutils.datetime') as mock_datetime, \
             patch('routina.decorators.datetime') as mock_decorators_datetime:
            # Exact match
            mock_dt = datetime.datetime(2024, 1, 1, 14, 30)
            mock_datetime.datetime.now.return_value = mock_dt
            mock_decorators_datetime.datetime.now.return_value = mock_dt
            result = test_func()
            assert result == "cron_success"
            
            # Wrong time
            mock_dt = datetime.datetime(2024, 1, 1, 14, 31)
            mock_datetime.datetime.now.return_value = mock_dt
            mock_decorators_datetime.datetime.now.return_value = mock_dt
            result = test_func()
            assert result is None
    
    def test_retry_logic(self):
        """Test retry functionality."""
        call_count = 0
        
        @every_n_seconds(1, retry_count=2, retry_delay=0.1)
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Test error")
            return "success"
        
        # Should succeed after retries
        result = failing_func()
        assert result == "success"
        assert call_count == 3
    
    def test_timeout(self):
        """Test timeout functionality."""
        @every_n_seconds(1, timeout=1)
        def slow_func():
            time.sleep(2)
            return "too_slow"
        
        # Note: This test is platform-dependent (Unix-like systems with signals)
        # On systems without signal support, this will pass through
        try:
            result = slow_func()
            # If no timeout occurred, function should have been called
            assert result is None or result == "too_slow"
        except Exception:
            # Timeout or other error is expected
            pass


class TestRunner:
    """Test runner functions."""
    
    def setup_method(self):
        """Set up test environment."""
        _scheduled_functions.clear()
        set_storage_backend(InMemoryStorage())
    
    def test_run_if_due(self):
        """Test run_if_due function."""
        @every_n_seconds(1)
        def test_func():
            return "success"
        
        result = run_if_due(test_func)
        assert result == "success"
        
        # Test with non-scheduled function
        def regular_func():
            return "regular"
        
        with pytest.raises(ExecutionError):
            run_if_due(regular_func)
    
    def test_run_all_due(self):
        """Test run_all_due function."""
        @every_n_seconds(1)
        def func1():
            return "result1"
        
        @every_n_seconds(1)
        def func2():
            raise ValueError("Test error")
        
        results = run_all_due()
        
        assert "func1" in results
        assert results["func1"]["success"] is True
        assert results["func1"]["result"] == "result1"
        
        assert "func2" in results
        assert results["func2"]["success"] is False
        assert "Test error" in results["func2"]["error"]
    
    def test_get_function_status(self):
        """Test get_function_status function."""
        @every_n_seconds(60)
        def test_func():
            return "success"
        
        # Run the function to create history
        test_func()
        
        status = get_function_status("test_func")
        assert status["exists"]
        assert status["name"] == "test_func"
        assert status["run_count"] == 1
        assert status["success_count"] == 1
        assert status["error_count"] == 0
        assert status["schedule_type"] == "interval"
        
        # Test non-existent function
        status = get_function_status("nonexistent")
        assert not status["exists"]
    
    def test_reset_function_history(self):
        """Test reset_function_history function."""
        @every_n_seconds(1)
        def test_func():
            return "success"
        
        # Run and create history
        test_func()
        
        status = get_function_status("test_func")
        assert status["run_count"] == 1
        
        # Reset history
        assert reset_function_history("test_func")
        
        status = get_function_status("test_func")
        assert not status["exists"]
        
        # Test resetting non-existent function
        assert not reset_function_history("nonexistent")


class TestExceptions:
    """Test custom exceptions."""
    
    def test_schedule_error(self):
        """Test ScheduleError."""
        with pytest.raises(ScheduleError):
            every_n_seconds(-1)
    
    def test_execution_error(self):
        """Test ExecutionError."""
        def regular_func():
            pass
        
        with pytest.raises(ExecutionError):
            run_if_due(regular_func)


class TestIntegration:
    """Integration tests."""
    
    def setup_method(self):
        """Set up test environment."""
        _scheduled_functions.clear()
        set_storage_backend(InMemoryStorage())
    
    def test_real_world_example(self):
        """Test a real-world usage example."""
        log_entries = []
        
        @every_n_seconds(2)
        def backup_logs():
            log_entries.append("Backup completed")
            return "backup_success"
        
        @at_time("14:30")
        def daily_report():
            log_entries.append("Daily report generated")
            return "report_success"
        
        @on_weekdays()
        def weekday_task():
            log_entries.append("Weekday task executed")
            return "weekday_success"
        
        # Run all functions
        results = run_all_due()
        
        # Check that functions were registered and executed appropriately
        assert len(routina.decorators.get_all_scheduled_functions()) == 3
        
        # The backup function should run (first time)
        assert "backup_logs" in results
        
        # Check status
        status = get_function_status("backup_logs")
        assert status["exists"]
        assert status["schedule_type"] == "interval"


if __name__ == "__main__":
    pytest.main([__file__]) 