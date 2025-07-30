"""Storage backends for routina."""

import json
import os
import sqlite3
import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from .exceptions import StorageError


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def should_run(self, name: str, interval_seconds: int) -> bool:
        """Check if function should run based on last execution time."""
        pass
    
    @abstractmethod
    def record_run(self, name: str, success: bool = True, error: Optional[str] = None) -> None:
        """Record function execution."""
        pass
    
    @abstractmethod
    def get_function_status(self, name: str) -> Dict[str, Any]:
        """Get status information for a function."""
        pass
    
    @abstractmethod
    def get_all_functions(self) -> List[str]:
        """Get list of all tracked functions."""
        pass
    
    @abstractmethod
    def reset_function(self, name: str) -> None:
        """Reset function history."""
        pass
    
    @abstractmethod
    def clear_all(self) -> None:
        """Clear all function history."""
        pass


class JSONStorage(StorageBackend):
    """JSON file-based storage backend."""
    
    def __init__(self, file_path: str = ".routina/state.json"):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure the directory exists."""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        try:
            if not os.path.exists(self.file_path):
                return {}
            
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise StorageError(f"Failed to load data from {self.file_path}: {e}")
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise StorageError(f"Failed to save data to {self.file_path}: {e}")
    
    def should_run(self, name: str, interval_seconds: int) -> bool:
        """Check if function should run."""
        with self._lock:
            data = self._load_data()
            function_data = data.get(name, {})
            
            last_run = function_data.get('last_run')
            if last_run is None:
                return True
            
            time_since_last = time.time() - last_run
            return time_since_last >= interval_seconds
    
    def record_run(self, name: str, success: bool = True, error: Optional[str] = None) -> None:
        """Record function execution."""
        with self._lock:
            data = self._load_data()
            
            if name not in data:
                data[name] = {
                    'first_run': time.time(),
                    'run_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                }
            
            function_data = data[name]
            function_data['last_run'] = time.time()
            function_data['run_count'] += 1
            
            if success:
                function_data['success_count'] += 1
                function_data.pop('last_error', None)
            else:
                function_data['error_count'] += 1
                function_data['last_error'] = error
                function_data['last_error_time'] = time.time()
            
            self._save_data(data)
    
    def get_function_status(self, name: str) -> Dict[str, Any]:
        """Get function status."""
        with self._lock:
            data = self._load_data()
            function_data = data.get(name, {})
            
            if not function_data:
                return {"exists": False}
            
            return {
                "exists": True,
                "first_run": function_data.get('first_run'),
                "last_run": function_data.get('last_run'),
                "run_count": function_data.get('run_count', 0),
                "success_count": function_data.get('success_count', 0),
                "error_count": function_data.get('error_count', 0),
                "last_error": function_data.get('last_error'),
                "last_error_time": function_data.get('last_error_time'),
            }
    
    def get_all_functions(self) -> List[str]:
        """Get all tracked functions."""
        with self._lock:
            data = self._load_data()
            return list(data.keys())
    
    def reset_function(self, name: str) -> None:
        """Reset function history."""
        with self._lock:
            data = self._load_data()
            if name in data:
                del data[name]
                self._save_data(data)
    
    def clear_all(self) -> None:
        """Clear all function history."""
        with self._lock:
            self._save_data({})


class SQLiteStorage(StorageBackend):
    """SQLite database storage backend."""
    
    def __init__(self, db_path: str = ".routina/state.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._ensure_directory()
        self._init_database()
    
    def _ensure_directory(self) -> None:
        """Ensure the directory exists."""
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS function_runs (
                        name TEXT PRIMARY KEY,
                        first_run REAL,
                        last_run REAL,
                        run_count INTEGER DEFAULT 0,
                        success_count INTEGER DEFAULT 0,
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        last_error_time REAL
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            raise StorageError(f"Failed to initialize database: {e}")
    
    def should_run(self, name: str, interval_seconds: int) -> bool:
        """Check if function should run."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT last_run FROM function_runs WHERE name = ?",
                        (name,)
                    )
                    result = cursor.fetchone()
                    
                    if result is None or result[0] is None:
                        return True
                    
                    time_since_last = time.time() - result[0]
                    return time_since_last >= interval_seconds
            except sqlite3.Error as e:
                raise StorageError(f"Database error in should_run: {e}")
    
    def record_run(self, name: str, success: bool = True, error: Optional[str] = None) -> None:
        """Record function execution."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    current_time = time.time()
                    
                    cursor = conn.execute(
                        "SELECT run_count, success_count, error_count FROM function_runs WHERE name = ?",
                        (name,)
                    )
                    result = cursor.fetchone()
                    
                    if result is None:
                        conn.execute("""
                            INSERT INTO function_runs 
                            (name, first_run, last_run, run_count, success_count, error_count, last_error, last_error_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            name, current_time, current_time, 1,
                            1 if success else 0, 0 if success else 1,
                            error if not success else None,
                            current_time if not success else None
                        ))
                    else:
                        run_count, success_count, error_count = result
                        new_success_count = success_count + (1 if success else 0)
                        new_error_count = error_count + (0 if success else 1)
                        
                        conn.execute("""
                            UPDATE function_runs 
                            SET last_run = ?, run_count = ?, success_count = ?, error_count = ?, 
                                last_error = ?, last_error_time = ?
                            WHERE name = ?
                        """, (
                            current_time, run_count + 1, new_success_count, new_error_count,
                            error if not success else None,
                            current_time if not success else None,
                            name
                        ))
                    
                    conn.commit()
            except sqlite3.Error as e:
                raise StorageError(f"Database error in record_run: {e}")
    
    def get_function_status(self, name: str) -> Dict[str, Any]:
        """Get function status."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT * FROM function_runs WHERE name = ?",
                        (name,)
                    )
                    result = cursor.fetchone()
                    
                    if result is None:
                        return {"exists": False}
                    
                    return {
                        "exists": True,
                        "first_run": result[1],
                        "last_run": result[2],
                        "run_count": result[3],
                        "success_count": result[4],
                        "error_count": result[5],
                        "last_error": result[6],
                        "last_error_time": result[7],
                    }
            except sqlite3.Error as e:
                raise StorageError(f"Database error in get_function_status: {e}")
    
    def get_all_functions(self) -> List[str]:
        """Get all tracked functions."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT name FROM function_runs")
                    return [row[0] for row in cursor.fetchall()]
            except sqlite3.Error as e:
                raise StorageError(f"Database error in get_all_functions: {e}")
    
    def reset_function(self, name: str) -> None:
        """Reset function history."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM function_runs WHERE name = ?", (name,))
                    conn.commit()
            except sqlite3.Error as e:
                raise StorageError(f"Database error in reset_function: {e}")
    
    def clear_all(self) -> None:
        """Clear all function history."""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM function_runs")
                    conn.commit()
            except sqlite3.Error as e:
                raise StorageError(f"Database error in clear_all: {e}")


class InMemoryStorage(StorageBackend):
    """In-memory storage backend for testing."""
    
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def should_run(self, name: str, interval_seconds: int) -> bool:
        """Check if function should run."""
        with self._lock:
            function_data = self._data.get(name, {})
            last_run = function_data.get('last_run')
            
            if last_run is None:
                return True
            
            time_since_last = time.time() - last_run
            return time_since_last >= interval_seconds
    
    def record_run(self, name: str, success: bool = True, error: Optional[str] = None) -> None:
        """Record function execution."""
        with self._lock:
            if name not in self._data:
                self._data[name] = {
                    'first_run': time.time(),
                    'run_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                }
            
            function_data = self._data[name]
            function_data['last_run'] = time.time()
            function_data['run_count'] += 1
            
            if success:
                function_data['success_count'] += 1
                function_data.pop('last_error', None)
                function_data.pop('last_error_time', None)
            else:
                function_data['error_count'] += 1
                function_data['last_error'] = error
                function_data['last_error_time'] = time.time()
    
    def get_function_status(self, name: str) -> Dict[str, Any]:
        """Get function status."""
        with self._lock:
            function_data = self._data.get(name, {})
            
            if not function_data:
                return {"exists": False}
            
            return {
                "exists": True,
                "first_run": function_data.get('first_run'),
                "last_run": function_data.get('last_run'),
                "run_count": function_data.get('run_count', 0),
                "success_count": function_data.get('success_count', 0),
                "error_count": function_data.get('error_count', 0),
                "last_error": function_data.get('last_error'),
                "last_error_time": function_data.get('last_error_time'),
            }
    
    def get_all_functions(self) -> List[str]:
        """Get all tracked functions."""
        with self._lock:
            return list(self._data.keys())
    
    def reset_function(self, name: str) -> None:
        """Reset function history."""
        with self._lock:
            if name in self._data:
                del self._data[name]
    
    def clear_all(self) -> None:
        """Clear all function history."""
        with self._lock:
            self._data.clear()


# Global storage backend instance
_storage_backend: StorageBackend = JSONStorage()


def set_storage_backend(backend: StorageBackend) -> None:
    """Set the global storage backend."""
    global _storage_backend
    _storage_backend = backend


def get_storage_backend() -> StorageBackend:
    """Get the current storage backend."""
    return _storage_backend


def clear_all_history() -> None:
    """Clear all function history."""
    _storage_backend.clear_all() 