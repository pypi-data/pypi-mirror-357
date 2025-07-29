# ZScheduler

A high-performance task scheduling application with both GUI and CLI interfaces for scheduling commands and Python scripts.

![List](images/list-task.png)

![Calendar](images/calendar-task.png)

![Statistics](images/stat-task.png)

## ✨ Features

- **🖥️ GUI Application**: Intuitive PyQt6-based interface with multiple views
- **⌨️ CLI Interface**: Command-line interface for automation and scripting
- **�️ Universal Scheduling**: Schedule any command, Python module, or browser task
- **�📅 Multiple Views**: List, Calendar, Timeline, and Statistics views
- **🎨 Themes**: Dark and Light themes for comfortable usage
- **🔔 System Tray**: Run in background with system tray integration
- **📊 Statistics**: Monitor execution statistics and performance metrics
- **⏰ Flexible Scheduling**: Interval, cron, and one-time schedules
- **🔄 Task Management**: Pause, resume, edit, and duplicate schedules
- **🐍 Python Integration**: Direct scheduling of Python modules and functions
- **🌐 Browser Automation**: Seamless integration with browser-launcher
- **🚀 Immediate Execution**: Run commands instantly with `--now` or `run-now`
- **🎯 Proper Execution**: Commands run naturally without output capture interference
- **🔄 Smart Lifecycle**: One-time tasks auto-remove, recurring tasks persist

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install zscheduler
```

### From Source

```bash
git clone https://github.com/mexyusef/zscheduler.git
cd zscheduler
pip install -r requirements.txt
```

## 🚀 Quick Start

### GUI Application

```bash
# After pip install
zscheduler

# Or alternatively
zscheduler-app
```

### CLI Interface

```bash
# After pip install - see all available commands
zscheduler-cli --help

# Schedule any system command
zscheduler-cli add-command --cmd "python backup.py" --name "Daily Backup" --cron "0 2 * * *"

# Schedule Python modules
zscheduler-cli add-python --module "myapp.tasks" --function "process" --name "Data Processing" --interval 3600

# Add a browser task
zscheduler-cli add-browser-task --browser firefox --profile "default" --url "https://gmail.com" --interval 1800

# Execute commands immediately
zscheduler-cli run-now "start cmd"
zscheduler-cli add-command --cmd "notepad" --name "Quick Note" --now

# List and manage schedules
zscheduler-cli list
zscheduler-cli run <schedule-id>
zscheduler-cli remove <schedule-id>
```

## 🖥️ GUI Application Usage

### Starting the GUI

```bash
# Using installed command
zscheduler

# From source
python run.py
```

### Creating Schedules

1. **Click "New"** in the toolbar or use **File > New Schedule**
2. **Fill in details**:
   - **Name**: Descriptive name for the schedule
   - **Command**: Command to execute (e.g., `python script.py`, `notepad.exe`)
   - **Type**: Choose from Interval, Cron, or One-time
   - **Parameters**: Set timing based on selected type

3. **Click "Save"** to create the schedule

### Managing Schedules

- **✏️ Edit**: Select a schedule and click "Edit" to modify
- **⏸️ Pause/Resume**: Control execution without deleting
- **🗑️ Delete**: Remove unwanted schedules
- **📋 Duplicate**: Create a copy of existing schedule
- **📤 Export/Import**: Save/load schedule configurations

### Views

- **📋 List View**: Tabular view of all schedules with status
- **📅 Calendar View**: Visualize schedules on calendar
- **📈 Timeline View**: Horizontal timeline of scheduled tasks
- **📊 Statistics**: Execution metrics and performance data

### Keyboard Shortcuts

- **Ctrl+Q**: Quit application
- **Ctrl+N**: New schedule
- **Ctrl+S**: Save configuration
- **Ctrl+E**: Edit selected schedule
- **F5**: Refresh schedules

## ⌨️ CLI Interface Usage

The CLI supports scheduling **any command**, **Python modules**, and **browser tasks** with flexible timing options.

### CLI Help Output

```bash
$ zscheduler-cli --help
usage: zscheduler-cli [-h] {add-command,add-python,add-browser-task,list,run,remove,run-now} ...

ZScheduler CLI - Schedule commands, Python modules, and browser tasks

positional arguments:
  {add-command,add-python,add-browser-task,list,run,remove,run-now}
                        Available commands
    add-command         Schedule any command or script
    add-python          Schedule Python modules or functions
    add-browser-task    Add a browser launch schedule
    list                List all schedules
    run                 Run a schedule immediately
    remove              Remove a schedule by ID
    run-now             Execute a command immediately without scheduling

options:
  -h, --help            show this help message and exit

Examples:
  # Schedule any command
  zscheduler-cli add-command --cmd "python backup.py" --name "Daily Backup" --cron "0 2 * * *"

  # Schedule Python module
  zscheduler-cli add-python --module "mymodule.main" --function "process_data" --interval 3600

  # Browser task
  zscheduler-cli add-browser-task --browser firefox --profile "default" --url "https://gmail.com" --interval 1800

  # One-time task
  zscheduler-cli add-command --cmd "shutdown /s /t 0" --once "2024-12-25T23:59:00" --name "Christmas Shutdown"

  # Run immediately without scheduling
  zscheduler-cli run-now "start cmd"

  # List and manage schedules
  zscheduler-cli list
  zscheduler-cli run abc123def456
  zscheduler-cli remove abc123def456
```

### Available Commands

```bash
# Schedule any system command
zscheduler-cli add-command [options]

# Schedule Python modules/functions
zscheduler-cli add-python [options]

# Schedule browser tasks
zscheduler-cli add-browser-task [options]

# Execute command immediately (no scheduling)
zscheduler-cli run-now <command>

# List all schedules
zscheduler-cli list

# Run schedule immediately
zscheduler-cli run <schedule_id>

# Remove schedule
zscheduler-cli remove <schedule_id>
```

### Scheduling System Commands

Schedule any command, script, or executable with flexible timing:

```bash
# Daily backup script
zscheduler-cli add-command \
  --cmd "python backup.py" \
  --name "Daily Backup" \
  --cron "0 2 * * *"

# System maintenance every Sunday at 3 AM
zscheduler-cli add-command \
  --cmd "cleanup.bat" \
  --name "Weekly Cleanup" \
  --cron "0 3 * * 0"

# One-time system shutdown
zscheduler-cli add-command \
  --cmd "shutdown /s /t 0" \
  --once "2024-12-25T23:59:00" \
  --name "Christmas Shutdown"

# Recurring log rotation every 6 hours
zscheduler-cli add-command \
  --cmd "logrotate /etc/logrotate.conf" \
  --interval 21600 \
  --name "Log Rotation"

# File synchronization every 30 minutes
zscheduler-cli add-command \
  --cmd "rsync -av /source/ /backup/" \
  --interval 1800 \
  --name "File Sync"

# Run immediately (new terminal)
zscheduler-cli add-command \
  --cmd "start cmd" \
  --name "New Terminal" \
  --now

# Execute without scheduling
zscheduler-cli run-now "start cmd"
zscheduler-cli run-now "notepad"
```

### Scheduling Python Modules

Schedule Python functions and modules with arguments:

```bash
# Data processing every hour
zscheduler-cli add-python \
  --module "myapp.tasks" \
  --function "process_data" \
  --interval 3600 \
  --name "Data Processing"

# Daily report generation at 8 AM
zscheduler-cli add-python \
  --module "reports.generator" \
  --function "daily_report" \
  --cron "0 8 * * *" \
  --name "Daily Report"

# One-time data migration with arguments
zscheduler-cli add-python \
  --module "migration.scripts" \
  --function "migrate_users" \
  --args '[100, "batch_1"]' \
  --kwargs '{"dry_run": false, "verbose": true}' \
  --once "2024-12-26T02:00:00" \
  --name "User Migration"

# Email notifications every 4 hours
zscheduler-cli add-python \
  --module "notifications.email" \
  --function "send_status_update" \
  --interval 14400 \
  --name "Status Notifications"

# Database cleanup weekly
zscheduler-cli add-python \
  --module "database.maintenance" \
  --function "cleanup_old_records" \
  --cron "0 1 * * 0" \
  --name "DB Cleanup"
```

### Scheduling Browser Tasks

```bash
# Basic browser task
zscheduler-cli add-browser-task \
  --browser firefox \
  --profile "default" \
  --url "https://gmail.com" \
  --name "Check Gmail"

# Recurring browser task (every 30 minutes)
zscheduler-cli add-browser-task \
  --browser chrome \
  --profile "work" \
  --url "https://calendar.google.com" \
  --interval 1800 \
  --name "Check Calendar"

# One-time browser task
zscheduler-cli add-browser-task \
  --browser firefox \
  --profile "personal" \
  --url "https://github.com" \
  --once "2024-12-25T09:00:00" \
  --name "Christmas GitHub Check"

# Cron-based browser task (weekdays at 9 AM)
zscheduler-cli add-browser-task \
  --browser firefox \
  --profile "work" \
  --url "https://mail.company.com" \
  --cron "0 9 * * 1-5" \
  --name "Work Email"

# Incognito mode
zscheduler-cli add-browser-task \
  --browser chrome \
  --profile "default" \
  --url "https://private-site.com" \
  --incognito \
  --name "Private Browsing"
```

### Managing Schedules via CLI

```bash
# List all schedules with details
zscheduler-cli list

# Run a specific schedule immediately (useful for testing)
zscheduler-cli run abc123def456

# Remove a schedule permanently
zscheduler-cli remove abc123def456

# Get detailed help for any command
zscheduler-cli add-command --help
zscheduler-cli add-python --help
zscheduler-cli add-browser-task --help
```

### Immediate Execution (New Features)

Execute commands immediately without scheduling:

```bash
# Execute any command right now (no scheduling)
zscheduler-cli run-now "start cmd"
zscheduler-cli run-now "notepad"
zscheduler-cli run-now "python script.py"

# Schedule to run immediately (adds to schedule, runs in 2 seconds, then removes)
zscheduler-cli add-command --cmd "start cmd" --name "New Terminal" --now
zscheduler-cli add-python --module "myapp" --function "test" --name "Quick Test" --now

# Open new terminal windows
zscheduler-cli run-now "start cmd"              # New cmd window
zscheduler-cli run-now "start cmd /k"           # New cmd window (stays open)
zscheduler-cli run-now "start powershell"       # New PowerShell window
zscheduler-cli run-now "start wt"               # New Windows Terminal (if installed)
```

### Task Lifecycle Management

ZScheduler now properly manages task lifecycles:

- **One-time tasks** (`--once`, `--now`): Automatically removed after execution
- **Recurring tasks** (`--interval`, `--cron`): Remain in schedule for future runs
- **Manual execution**: Use `zscheduler-cli run <id>` to test any scheduled task

### Detailed Command Help

#### add-command Help
```bash
$ zscheduler-cli add-command --help
usage: zscheduler-cli add-command [-h] --cmd CMD --name NAME [--interval INTERVAL]
                                  [--once ONCE] [--cron CRON] [--now] [--enabled]

Schedule any system command, script, or executable

options:
  -h, --help           show this help message and exit
  --cmd CMD            Command to execute (e.g., 'python script.py', 'backup.bat')
  --name NAME          Descriptive name for the task
  --interval INTERVAL  Interval in seconds for recurring tasks
  --once ONCE          Run once at specific datetime (ISO format: YYYY-MM-DDTHH:MM:SS)
  --cron CRON          Cron expression for advanced scheduling
  --now                Run immediately (schedules to run in 2 seconds)
  --enabled            Enable the schedule immediately
```

#### add-python Help
```bash
$ zscheduler-cli add-python --help
usage: zscheduler-cli add-python [-h] --module MODULE --function FUNCTION [--args ARGS]
                                 [--kwargs KWARGS] --name NAME [--interval INTERVAL]
                                 [--once ONCE] [--cron CRON] [--now] [--enabled]

Schedule Python modules, functions, or methods to run

options:
  -h, --help           show this help message and exit
  --module MODULE      Python module path (e.g., 'myapp.tasks')
  --function FUNCTION  Function name to call
  --args ARGS          JSON string of positional arguments (e.g., '[1, "hello"]')
  --kwargs KWARGS      JSON string of keyword arguments (e.g., '{"key": "value"}')
  --name NAME          Descriptive name for the task
  --interval INTERVAL  Interval in seconds for recurring tasks
  --once ONCE          Run once at specific datetime (ISO format: YYYY-MM-DDTHH:MM:SS)
  --cron CRON          Cron expression for advanced scheduling
  --now                Run immediately (schedules to run in 2 seconds)
  --enabled            Enable the schedule immediately
```

### Scheduling Options

All command types support flexible scheduling:

- **Immediate execution**: `--now` (runs in 2 seconds)
- **Interval-based**: `--interval 3600` (every hour)
- **Cron expressions**: `--cron "0 9 * * 1-5"` (weekdays at 9 AM)
- **One-time execution**: `--once "2024-12-25T10:00:00"` (specific datetime)

#### Common Cron Patterns
```bash
# Every minute
--cron "* * * * *"

# Every hour at minute 0
--cron "0 * * * *"

# Daily at 2:30 AM
--cron "30 2 * * *"

# Weekly on Sunday at midnight
--cron "0 0 * * 0"

# Monthly on the 1st at 6 AM
--cron "0 6 1 * *"

# Weekdays at 9 AM
--cron "0 9 * * 1-5"
```

## 📁 Configuration

ZScheduler stores configuration and data in your home directory:

- **`~/.zscheduler/config.json`**: Application settings and preferences
- **`~/.zscheduler/schedules.json`**: Saved schedules and tasks
- **`~/.zscheduler/logs/zscheduler.log`**: Application logs and debug info

## 🔧 Advanced Usage

### Integration with browser-launcher

ZScheduler works seamlessly with [browser-launcher](https://github.com/mexyusef/browser-launcher) for managing browser profiles:

```bash
# List Firefox profiles
browser-launcher list-profiles --browser firefox

# Schedule multiple profiles
zscheduler-cli add-browser-task --browser firefox --profile "profile1" --url "https://gmail.com"
zscheduler-cli add-browser-task --browser firefox --profile "profile2" --url "https://calendar.google.com"
```

### Batch Operations

Create multiple schedules using scripts:

```bash
#!/bin/bash
# Schedule multiple Gmail accounts
profiles=("work" "personal" "backup")
for profile in "${profiles[@]}"; do
  zscheduler-cli add-browser-task \
    --browser firefox \
    --profile "$profile" \
    --url "https://mail.google.com" \
    --interval 3600 \
    --name "Gmail $profile"
done

# Schedule multiple backup tasks
backup_dirs=("/home/user/documents" "/home/user/projects" "/home/user/photos")
for dir in "${backup_dirs[@]}"; do
  dir_name=$(basename "$dir")
  zscheduler-cli add-command \
    --cmd "rsync -av '$dir' /backup/" \
    --cron "0 2 * * *" \
    --name "Backup $dir_name"
done

# Schedule multiple Python data processing tasks
modules=("analytics.daily" "analytics.weekly" "analytics.monthly")
crons=("0 1 * * *" "0 2 * * 0" "0 3 1 * *")
for i in "${!modules[@]}"; do
  zscheduler-cli add-python \
    --module "${modules[$i]}" \
    --function "generate_report" \
    --cron "${crons[$i]}" \
    --name "Report ${modules[$i]}"
done
```

### System Integration

#### Windows Task Scheduler
```batch
# Run ZScheduler at startup
schtasks /create /tn "ZScheduler" /tr "zscheduler" /sc onstart
```

#### Linux Systemd
```ini
# ~/.config/systemd/user/zscheduler.service
[Unit]
Description=ZScheduler Task Manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/local/bin/zscheduler
Restart=always

[Install]
WantedBy=default.target
```

## 🛠️ Development

### Project Structure

```
zscheduler/
├── pyproject.toml          # Package configuration
├── README.md               # This documentation
├── LICENSE                 # MIT License
├── requirements.txt        # Dependencies
├── run.py                  # Development launcher
├── zscheduler_app/         # Main application package
│   ├── main.py             # GUI entry point
│   ├── cli/                # CLI interface
│   │   └── cli.py          # CLI commands
│   ├── config/             # Configuration management
│   ├── data/               # Data persistence
│   ├── scheduler/          # Core scheduling logic
│   ├── themes/             # UI themes and styling
│   └── ui/                 # GUI components
└── zscheduler_lib/         # Core scheduling library
    └── zscheduler/         # Library modules
        ├── core/           # Core scheduling classes
        ├── tasks/          # Task types
        ├── events/         # Event system
        └── utils/          # Utilities
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/mexyusef/zscheduler.git
cd zscheduler

# Install dependencies
pip install -r requirements.txt

# Run from source
python run.py                    # GUI
python -m zscheduler_app.cli.cli # CLI

# Build package
python -m build

# Install locally
pip install dist/zscheduler-*.whl
```

### Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Commit** changes: `git commit -am 'Add feature'`
4. **Push** to branch: `git push origin feature-name`
5. **Submit** a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🚀 Future Plans

- **🔌 Plugin System**: Extensible architecture for custom functionality
- **🌐 Web Interface**: Browser-based management interface
- **📱 Mobile App**: Companion mobile application
- **☁️ Cloud Sync**: Synchronize schedules across devices
- **🤖 AI Integration**: Smart scheduling suggestions
- **📈 Advanced Analytics**: Detailed performance insights
- **🔗 API Integration**: REST API for external integrations

## 🆘 Support

- **📖 Documentation**: [GitHub Wiki](https://github.com/mexyusef/zscheduler/wiki)
- **🐛 Issues**: [GitHub Issues](https://github.com/mexyusef/zscheduler/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/mexyusef/zscheduler/discussions)

## 🏷️ Version

Current version: **0.0.3**

### What's New in v0.0.3

#### 🚀 **Major CLI Enhancements**
- **Universal Command Scheduling**: Schedule any system command, not just browser tasks
- **Python Module Scheduling**: Direct scheduling of Python functions with arguments
- **Immediate Execution**: New `--now` flag and `run-now` command for instant execution
- **Enhanced Help**: Comprehensive help with practical examples for all commands

#### 🎯 **Scheduler Improvements**
- **Proper Command Execution**: Fixed scheduler to run commands naturally without output capture
- **Smart Task Lifecycle**: One-time tasks automatically removed after execution
- **GUI Applications Support**: Commands like `notepad`, `start cmd` now work correctly
- **Terminal Window Support**: Can properly open new terminal windows

#### 🛠️ **Technical Fixes**
- **Argument Naming**: Fixed `--command` vs `args.command` conflict (now uses `--cmd`)
- **Execution Engine**: Removed `capture_output=True` to allow GUI apps to show windows
- **Task Management**: Proper handling of recurring vs one-time task lifecycles

#### 📋 **New CLI Commands**
```bash
# New universal command scheduling
zscheduler-cli add-command --cmd "any command" --name "task" [timing options]

# New Python module scheduling
zscheduler-cli add-python --module "mymodule" --function "func" --name "task" [timing options]

# New immediate execution
zscheduler-cli run-now "command"
zscheduler-cli add-command --cmd "command" --name "task" --now
```

For detailed changelog and release notes, see [Releases](https://github.com/mexyusef/zscheduler/releases).
