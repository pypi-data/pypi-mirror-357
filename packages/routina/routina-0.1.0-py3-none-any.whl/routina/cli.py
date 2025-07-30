"""Command-line interface for routina."""

import argparse
import sys
from typing import Optional
from .runner import (
    print_status_report,
    list_scheduled_functions,
    get_function_status,
    reset_function_history,
    force_run,
    run_all_due,
)
from .store import set_storage_backend, JSONStorage, SQLiteStorage, InMemoryStorage, clear_all_history
from .exceptions import RoutinaError


def main() -> None:
    """entry point.."""
    parser = argparse.ArgumentParser(
        description="Routina - A Python-native, time-aware function runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  routina status                    # Show status of all scheduled functions
  routina list                      # List all scheduled functions
  routina status my_function        # Show status of specific function
  routina run                       # Run all due functions
  routina force my_function         # Force run a specific function
  routina reset my_function         # Reset function history
  routina clear                     # Clear all history
        """
    )
    
    parser.add_argument(
        "--storage", 
        choices=["json", "sqlite", "memory"],
        default="json",
        help="Storage backend to use (default: json)"
    )
    
    parser.add_argument(
        "--storage-path",
        help="Path for storage file (default: .routina/state.json or .routina/state.db)"
    )
    
    # commands for the cli
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    status_parser = subparsers.add_parser("status", help="Show function status")
    status_parser.add_argument("function", nargs="?", help="Specific function name")
    
    subparsers.add_parser("list", help="List all scheduled functions")
    
    subparsers.add_parser("run", help="Run all due functions")
    
    force_parser = subparsers.add_parser("force", help="Force run a function")
    force_parser.add_argument("function", help="Function name to force run")
    
    reset_parser = subparsers.add_parser("reset", help="Reset function history")
    reset_parser.add_argument("function", help="Function name to reset")
    
    subparsers.add_parser("clear", help="Clear all function history")
    
    args = parser.parse_args()
    
    try:
        if args.storage == "json":
            path = args.storage_path or ".routina/state.json"
            set_storage_backend(JSONStorage(path))
        elif args.storage == "sqlite":
            path = args.storage_path or ".routina/state.db"
            set_storage_backend(SQLiteStorage(path))
        elif args.storage == "memory":
            set_storage_backend(InMemoryStorage())
    except Exception as e:
        print(f"Error setting up storage: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.command == "status":
            if args.function:
                status = get_function_status(args.function)
                if not status.get("exists"):
                    print(f"Function '{args.function}' not found.")
                    sys.exit(1)
                
                print(f"Status for {args.function}:")
                print(f"  Runs: {status.get('run_count', 0)}")
                print(f"  Success: {status.get('success_count', 0)}")
                print(f"  Errors: {status.get('error_count', 0)}")
                
                if status.get('success_rate') is not None:
                    print(f"  Success Rate: {status['success_rate']:.1%}")
                
                if status.get('last_run_human'):
                    print(f"  Last Run: {status['last_run_human']}")
                
                if status.get('next_run_human'):
                    print(f"  Next Run: {status['next_run_human']}")
                
                if status.get('last_error'):
                    print(f"  Last Error: {status['last_error']}")
            else:
                print_status_report()
        
        elif args.command == "list":
            functions = list_scheduled_functions()
            if not functions:
                print("No scheduled functions found.")
            else:
                print("Scheduled Functions:")
                for func in functions:
                    print(f"  📋 {func['name']} ({func['schedule_type']})")
                    print(f"     Module: {func['module']}")
        
        elif args.command == "run":
            print("Running all due functions...")
            results = run_all_due()
            
            if not results:
                print("No functions were due to run.")
            else:
                for func_name, result in results.items():
                    if result['success']:
                        print(f"✅ {func_name}: Success")
                    else:
                        print(f"❌ {func_name}: {result['error']}")
        
        elif args.command == "force":
            print(f"Force running {args.function}...")
            try:
                result = force_run(args.function)
                print(f"✅ {args.function}: Success")
                if result is not None:
                    print(f"   Result: {result}")
            except Exception as e:
                print(f"❌ {args.function}: {e}")
                sys.exit(1)
        
        elif args.command == "reset":
            if reset_function_history(args.function):
                print(f"✅ Reset history for {args.function}")
            else:
                print(f"❌ Function '{args.function}' not found")
                sys.exit(1)
        
        elif args.command == "clear":
            confirm = input("Are you sure you want to clear all function history? (y/N): ")
            if confirm.lower() in ['y', 'yes']:
                clear_all_history()
                print("✅ Cleared all function history")
            else:
                print("Cancelled")
        
        else:
            parser.print_help()
    
    except RoutinaError as e:
        print(f"Routina error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 