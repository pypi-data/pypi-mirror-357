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
    parser = argparse.ArgumentParser(description="ZScheduler CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Add browser task
    add_browser = subparsers.add_parser("add-browser-task", help="Add a browser launch schedule")
    add_browser.add_argument("--browser", required=True, help="Browser type (e.g., firefox, chrome)")
    add_browser.add_argument("--profile", required=True, help="Browser profile name or path")
    add_browser.add_argument("--url", required=True, help="URL to open")
    add_browser.add_argument("--name", default=None, help="Task name")
    add_browser.add_argument("--interval", type=int, default=None, help="Interval in seconds (for recurring)")
    add_browser.add_argument("--once", default=None, help="Run once at datetime (ISO format)")
    add_browser.add_argument("--cron", default=None, help="Cron expression (for cron schedule)")
    add_browser.add_argument("--incognito", action="store_true", help="Launch in incognito/private mode")
    add_browser.add_argument("--enabled", action="store_true", help="Enable the schedule (default: enabled)")

    # List schedules
    list_parser = subparsers.add_parser("list", help="List all schedules")

    # Run schedule now
    run_parser = subparsers.add_parser("run", help="Run a schedule immediately")
    run_parser.add_argument("schedule_id", help="ID of the schedule to run")

    # Remove schedule
    remove_parser = subparsers.add_parser("remove", help="Remove a schedule by ID")
    remove_parser.add_argument("schedule_id", help="ID of the schedule to remove")

    args = parser.parse_args()

    # Load config and schedules
    app_config = AppConfig(CONFIG_PATH)
    json_store = JsonStore(SCHEDULES_PATH)
    scheduler = Scheduler()
    schedules = json_store.load()
    for sched in schedules:
        scheduler.add_schedule(sched)

    if args.command == "add-browser-task":
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
        try:
            cmd_args = json.loads(cmd)
        except Exception:
            print(f"Invalid command format for schedule {args.schedule_id}. Cannot run.")
            sys.exit(1)
        if cmd_args and cmd_args[0] == "launch_browser":
            if BrowserProfileManager is None:
                print("browser_launcher library is not installed. Cannot launch browser.")
                sys.exit(1)
            parser = argparse.ArgumentParser()
            parser.add_argument("--browser", required=True)
            parser.add_argument("--profile", required=True)
            parser.add_argument("--url", required=True)
            parser.add_argument("--incognito", action="store_true")
            try:
                args2 = parser.parse_args(cmd_args[1:])
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
        else:
            print(f"Would execute: {cmd}")
            # Here you could add support for other command types
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
