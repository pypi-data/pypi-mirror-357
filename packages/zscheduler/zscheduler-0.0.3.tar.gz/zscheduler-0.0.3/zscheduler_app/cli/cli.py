import argparse
import sys
from pathlib import Path
from zscheduler_app.config.app_config import AppConfig
from zscheduler_app.data.json_store import JsonStore
from zscheduler_app.scheduler.scheduler import Scheduler
from datetime import datetime
import shlex
import json

# Import browser_launcher if available
try:
    from browser_launcher.profile_manager import BrowserProfileManager, LaunchOptions
except ImportError:
    BrowserProfileManager = None
    LaunchOptions = None

CONFIG_PATH = str(Path.home() / ".zscheduler" / "config.json")
SCHEDULES_PATH = str(Path.home() / ".zscheduler" / "schedules.json")

def main():
    parser = argparse.ArgumentParser(
        description="ZScheduler CLI - Schedule commands, Python modules, and browser tasks",
        epilog="""
Examples:
  # Schedule any command
  zscheduler-cli add-command --command "python backup.py" --name "Daily Backup" --cron "0 2 * * *"

  # Schedule Python module
  zscheduler-cli add-python --module "mymodule.main" --function "process_data" --interval 3600

  # Browser task
  zscheduler-cli add-browser-task --browser firefox --profile "default" --url "https://gmail.com" --interval 1800

  # One-time task
  zscheduler-cli add-command --command "shutdown /s /t 0" --once "2024-12-25T23:59:00" --name "Christmas Shutdown"

  # List and manage schedules
  zscheduler-cli list
  zscheduler-cli run abc123def456
  zscheduler-cli remove abc123def456
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add general command
    add_command = subparsers.add_parser(
        "add-command",
        help="Schedule any command or script",
        description="Schedule any system command, script, or executable",
        epilog="""
Examples:
  # Daily backup script
  zscheduler-cli add-command --command "python backup.py" --name "Daily Backup" --cron "0 2 * * *"

  # System maintenance every Sunday
  zscheduler-cli add-command --command "cleanup.bat" --name "Weekly Cleanup" --cron "0 3 * * 0"

  # One-time system shutdown
  zscheduler-cli add-command --command "shutdown /s /t 0" --once "2024-12-25T23:59:00" --name "Christmas Shutdown"

  # Recurring log rotation every 6 hours
  zscheduler-cli add-command --command "logrotate /etc/logrotate.conf" --interval 21600 --name "Log Rotation"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    add_command.add_argument("--command", required=True, help="Command to execute (e.g., 'python script.py', 'backup.bat')")
    add_command.add_argument("--name", required=True, help="Descriptive name for the task")
    add_command.add_argument("--interval", type=int, default=None, help="Interval in seconds for recurring tasks")
    add_command.add_argument("--once", default=None, help="Run once at specific datetime (ISO format: YYYY-MM-DDTHH:MM:SS)")
    add_command.add_argument("--cron", default=None, help="Cron expression for advanced scheduling")
    add_command.add_argument("--enabled", action="store_true", default=True, help="Enable the schedule immediately")

    # Add Python module/function
    add_python = subparsers.add_parser(
        "add-python",
        help="Schedule Python modules or functions",
        description="Schedule Python modules, functions, or methods to run",
        epilog="""
Examples:
  # Run a module function every hour
  zscheduler-cli add-python --module "myapp.tasks" --function "process_data" --interval 3600 --name "Data Processing"

  # Daily report generation
  zscheduler-cli add-python --module "reports.generator" --function "daily_report" --cron "0 8 * * *" --name "Daily Report"

  # One-time data migration
  zscheduler-cli add-python --module "migration.scripts" --function "migrate_users" --once "2024-12-26T02:00:00" --name "User Migration"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    add_python.add_argument("--module", required=True, help="Python module path (e.g., 'myapp.tasks')")
    add_python.add_argument("--function", required=True, help="Function name to call")
    add_python.add_argument("--args", default="", help="JSON string of positional arguments (e.g., '[1, \"hello\"]')")
    add_python.add_argument("--kwargs", default="{}", help="JSON string of keyword arguments (e.g., '{\"key\": \"value\"}')")
    add_python.add_argument("--name", required=True, help="Descriptive name for the task")
    add_python.add_argument("--interval", type=int, default=None, help="Interval in seconds for recurring tasks")
    add_python.add_argument("--once", default=None, help="Run once at specific datetime (ISO format: YYYY-MM-DDTHH:MM:SS)")
    add_python.add_argument("--cron", default=None, help="Cron expression for advanced scheduling")
    add_python.add_argument("--enabled", action="store_true", default=True, help="Enable the schedule immediately")

    # Add browser task
    add_browser = subparsers.add_parser(
        "add-browser-task",
        help="Add a browser launch schedule",
        description="Schedule a browser to launch with specific profile and URL",
        epilog="""
Examples:
  # Basic Gmail check
  zscheduler-cli add-browser-task --browser firefox --profile "default" --url "https://gmail.com" --name "Check Gmail"

  # Recurring calendar check every hour
  zscheduler-cli add-browser-task --browser chrome --profile "work" --url "https://calendar.google.com" --interval 3600 --name "Calendar Check"

  # Daily work email at 9 AM (Monday-Friday)
  zscheduler-cli add-browser-task --browser firefox --profile "work" --url "https://mail.company.com" --cron "0 9 * * 1-5" --name "Work Email"

  # One-time reminder
  zscheduler-cli add-browser-task --browser chrome --profile "personal" --url "https://reminder-site.com" --once "2024-12-25T10:00:00" --name "Christmas Reminder"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    add_browser.add_argument("--browser", required=True, help="Browser type (firefox, chrome, edge, safari)")
    add_browser.add_argument("--profile", required=True, help="Browser profile name (use 'browser-launcher list-profiles' to see available profiles)")
    add_browser.add_argument("--url", required=True, help="URL to open (e.g., https://gmail.com)")
    add_browser.add_argument("--name", default=None, help="Descriptive name for the task (auto-generated if not provided)")
    add_browser.add_argument("--interval", type=int, default=None, help="Interval in seconds for recurring tasks (e.g., 3600 for hourly)")
    add_browser.add_argument("--once", default=None, help="Run once at specific datetime (ISO format: YYYY-MM-DDTHH:MM:SS)")
    add_browser.add_argument("--cron", default=None, help="Cron expression for advanced scheduling (e.g., '0 9 * * 1-5' for weekdays at 9 AM)")
    add_browser.add_argument("--incognito", action="store_true", help="Launch in incognito/private browsing mode")
    add_browser.add_argument("--enabled", action="store_true", help="Enable the schedule immediately (default: enabled)")

    # List schedules
    list_parser = subparsers.add_parser(
        "list",
        help="List all schedules",
        description="Display all scheduled tasks with their details"
    )

    # Run schedule now
    run_parser = subparsers.add_parser(
        "run",
        help="Run a schedule immediately",
        description="Execute a specific schedule right now (useful for testing)"
    )
    run_parser.add_argument("schedule_id", help="ID of the schedule to run (get from 'list' command)")

    # Remove schedule
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove a schedule by ID",
        description="Permanently delete a scheduled task"
    )
    remove_parser.add_argument("schedule_id", help="ID of the schedule to remove (get from 'list' command)")

    args = parser.parse_args()

    # Load config and schedules
    app_config = AppConfig(CONFIG_PATH)
    json_store = JsonStore(SCHEDULES_PATH)
    scheduler = Scheduler()
    schedules = json_store.load()
    for sched in schedules:
        scheduler.add_schedule(sched)

    if args.command == "add-command":
        # Add general command schedule
        schedule_type = "interval" if args.interval else "once" if args.once else "cron" if args.cron else "interval"
        schedule_data = {
            "name": args.name,
            "command": args.command,
            "schedule_type": schedule_type,
            "enabled": args.enabled,
        }
        if args.interval:
            schedule_data["interval"] = args.interval
        if args.once:
            try:
                dt = datetime.fromisoformat(args.once)
                schedule_data["next_run"] = dt.isoformat()
                schedule_data["schedule_type"] = "once"
            except Exception:
                print("Invalid datetime format for --once. Use ISO format: YYYY-MM-DDTHH:MM:SS")
                sys.exit(1)
        if args.cron:
            schedule_data["cron_expression"] = args.cron
            schedule_data["schedule_type"] = "cron"

        schedule_id = scheduler.add_schedule(schedule_data)
        json_store.save(scheduler.get_schedules())
        print(f"Added command schedule '{args.name}' with ID: {schedule_id}")
        print(f"Command: {args.command}")
        print(f"Schedule type: {schedule_type}")

    elif args.command == "add-python":
        # Add Python module/function schedule
        try:
            args_list = json.loads(args.args) if args.args else []
            kwargs_dict = json.loads(args.kwargs) if args.kwargs else {}
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in args or kwargs: {e}")
            sys.exit(1)

        # Create a command that represents the Python call
        python_cmd = {
            "type": "python",
            "module": args.module,
            "function": args.function,
            "args": args_list,
            "kwargs": kwargs_dict
        }

        schedule_type = "interval" if args.interval else "once" if args.once else "cron" if args.cron else "interval"
        schedule_data = {
            "name": args.name,
            "command": json.dumps(python_cmd),
            "schedule_type": schedule_type,
            "enabled": args.enabled,
        }
        if args.interval:
            schedule_data["interval"] = args.interval
        if args.once:
            try:
                dt = datetime.fromisoformat(args.once)
                schedule_data["next_run"] = dt.isoformat()
                schedule_data["schedule_type"] = "once"
            except Exception:
                print("Invalid datetime format for --once. Use ISO format: YYYY-MM-DDTHH:MM:SS")
                sys.exit(1)
        if args.cron:
            schedule_data["cron_expression"] = args.cron
            schedule_data["schedule_type"] = "cron"

        schedule_id = scheduler.add_schedule(schedule_data)
        json_store.save(scheduler.get_schedules())
        print(f"Added Python schedule '{args.name}' with ID: {schedule_id}")
        print(f"Module: {args.module}")
        print(f"Function: {args.function}")
        print(f"Schedule type: {schedule_type}")

    elif args.command == "add-browser-task":
        # Store the command as a JSON-encoded list of arguments
        cmd_args = [
            "launch_browser",
            "--browser", args.browser,
            "--profile", args.profile,
            "--url", args.url
        ]
        if args.incognito:
            cmd_args.append("--incognito")
        cmd = json.dumps(cmd_args)
        name = args.name or f"{args.browser} {args.profile} {args.url}"
        enabled = args.enabled or True
        schedule_type = "interval" if args.interval else "once" if args.once else "cron" if args.cron else "interval"
        schedule_data = {
            "name": name,
            "command": cmd,
            "schedule_type": schedule_type,
            "enabled": enabled,
        }
        if args.interval:
            schedule_data["interval"] = args.interval
        if args.once:
            try:
                dt = datetime.fromisoformat(args.once)
                schedule_data["cron_expression"] = dt.isoformat()
            except Exception:
                print("Invalid datetime format for --once. Use ISO format.")
                sys.exit(1)
        if args.cron:
            schedule_data["cron_expression"] = args.cron
        schedule_id = scheduler.add_schedule(schedule_data)
        json_store.save(scheduler.get_schedules())
        print(f"Added browser schedule with ID: {schedule_id}")

    elif args.command == "list":
        all_scheds = scheduler.get_schedules()
        if not all_scheds:
            print("No schedules found.")
        else:
            for sched in all_scheds:
                print(f"ID: {sched['id']} | Name: {sched['name']} | Type: {sched['schedule_type']} | Command: {sched['command']} | Enabled: {sched['enabled']}")

    elif args.command == "run":
        sched = scheduler.get_schedule(args.schedule_id)
        if not sched:
            print(f"Schedule with ID {args.schedule_id} not found.")
            sys.exit(1)

        cmd = sched["command"]
        print(f"Running schedule: {sched['name']}")

        # Try to parse as JSON first (for structured commands)
        try:
            cmd_data = json.loads(cmd)

            # Handle browser tasks
            if isinstance(cmd_data, list) and cmd_data and cmd_data[0] == "launch_browser":
                if BrowserProfileManager is None:
                    print("browser_launcher library is not installed. Cannot launch browser.")
                    sys.exit(1)
                parser = argparse.ArgumentParser()
                parser.add_argument("--browser", required=True)
                parser.add_argument("--profile", required=True)
                parser.add_argument("--url", required=True)
                parser.add_argument("--incognito", action="store_true")
                try:
                    args2 = parser.parse_args(cmd_data[1:])
                except Exception as e:
                    print(f"Failed to parse browser launch command: {e}")
                    sys.exit(1)
                mgr = BrowserProfileManager()
                options = LaunchOptions(incognito=args2.incognito)
                print(f"Launching {args2.browser} with profile '{args2.profile}' and URL '{args2.url}'" + (" in incognito mode" if args2.incognito else ""))
                mgr.launch_browser(
                    browser_type=args2.browser,
                    profile=args2.profile,
                    url=args2.url,
                    options=options
                )

            # Handle Python tasks
            elif isinstance(cmd_data, dict) and cmd_data.get("type") == "python":
                module_name = cmd_data["module"]
                function_name = cmd_data["function"]
                args_list = cmd_data.get("args", [])
                kwargs_dict = cmd_data.get("kwargs", {})

                print(f"Executing Python function: {module_name}.{function_name}")
                print(f"Args: {args_list}")
                print(f"Kwargs: {kwargs_dict}")

                try:
                    # Import the module and get the function
                    import importlib
                    module = importlib.import_module(module_name)
                    func = getattr(module, function_name)

                    # Call the function
                    result = func(*args_list, **kwargs_dict)
                    print(f"Function executed successfully. Result: {result}")
                except ImportError as e:
                    print(f"Failed to import module {module_name}: {e}")
                    sys.exit(1)
                except AttributeError as e:
                    print(f"Function {function_name} not found in module {module_name}: {e}")
                    sys.exit(1)
                except Exception as e:
                    print(f"Error executing function: {e}")
                    sys.exit(1)

            else:
                print(f"Unknown structured command format: {cmd_data}")
                sys.exit(1)

        except json.JSONDecodeError:
            # Not JSON, treat as plain command
            print(f"Executing command: {cmd}")
            try:
                import subprocess
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                print(f"Command executed with return code: {result.returncode}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
            except Exception as e:
                print(f"Error executing command: {e}")
                sys.exit(1)
    elif args.command == "remove":
        removed = scheduler.remove_schedule(args.schedule_id)
        if removed:
            json_store.save(scheduler.get_schedules())
            print(f"Removed schedule with ID: {args.schedule_id}")
        else:
            print(f"Schedule with ID {args.schedule_id} not found.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
