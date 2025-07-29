# ZScheduler

A high-performance task scheduling application with both GUI and CLI interfaces for scheduling commands and Python scripts.

![List](images/list-task.png)

![Calendar](images/calendar-task.png)

![Statistics](images/stat-task.png)

## ✨ Features

- **🖥️ GUI Application**: Intuitive PyQt6-based interface with multiple views
- **⌨️ CLI Interface**: Command-line interface for automation and scripting
- **📅 Multiple Views**: List, Calendar, Timeline, and Statistics views
- **🎨 Themes**: Dark and Light themes for comfortable usage
- **🔔 System Tray**: Run in background with system tray integration
- **📊 Statistics**: Monitor execution statistics and performance metrics
- **⏰ Flexible Scheduling**: Interval, cron, and one-time schedules
- **🔄 Task Management**: Pause, resume, edit, and duplicate schedules

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
# After pip install
zscheduler-cli --help

# List all schedules
zscheduler-cli list

# Add a browser task
zscheduler-cli add-browser-task --browser firefox --profile "default" --url "https://gmail.com"
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

### Available Commands

```bash
# Show help
zscheduler-cli --help

# List all schedules
zscheduler-cli list

# Add browser task
zscheduler-cli add-browser-task [options]

# Run schedule immediately
zscheduler-cli run <schedule_id>

# Remove schedule
zscheduler-cli remove <schedule_id>
```

### Adding Browser Tasks

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

# Run a specific schedule now
zscheduler-cli run abc123def456

# Remove a schedule
zscheduler-cli remove abc123def456
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

Current version: **0.0.2**

For changelog and release notes, see [Releases](https://github.com/mexyusef/zscheduler/releases).
