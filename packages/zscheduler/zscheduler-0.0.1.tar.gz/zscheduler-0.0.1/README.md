# ZScheduler

A simple task scheduling application for commands and python.

![List](images/list-task.png)

![Calendar](images/calendar-task.png)

![Statistics](images/stat-task.png)

## Features

- **Multiple Views**: List, Calendar, Timeline, and Statistics views
- **Dark and Light Themes**: Choose your preferred theme for comfortable usage
- **System Tray Integration**: Run in the background while maintaining access
- **Statistics and Insights**: Monitor your scheduled tasks with detailed statistics
- **Flexible Scheduling Options**: Interval-based, cron-based, or one-time schedules

## Requirements

- Python 3.8+
- PyQt6
- Standard Python libraries (datetime, threading, json, etc.)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/mexyusef/zscheduler.git
cd zscheduler
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

You can run the application using the provided launcher script:

```bash
python run.py
```

Or directly:

```bash
python -m zscheduler_app.main
```

## Configuration

ZScheduler stores configuration files and schedules in the user's home directory:

- `~/.zscheduler/config.json`: Application configuration
- `~/.zscheduler/schedules.json`: Saved schedules
- `~/.zscheduler/logs/zscheduler.log`: Application logs

## Usage

### Creating a Schedule

1. Click the "New" button in the toolbar or use the menu "File > New Schedule"
2. Enter schedule details:
   - Name: A descriptive name for the schedule
   - Command: The command to execute
   - Type: Interval, Cron, or One-time
   - Additional parameters based on the type
3. Click "Save" to create the schedule

### Managing Schedules

- **Edit**: Select a schedule and click "Edit" to modify its properties
- **Pause/Resume**: Control the execution of schedules without removing them
- **Delete**: Remove unwanted schedules
- **Duplicate**: Create a copy of an existing schedule

### Views

- **List View**: Simple tabular view of all schedules
- **Calendar View**: Visualize schedules on a calendar
- **Timeline View**: See schedules on a horizontal timeline
- **Statistics**: Monitor execution statistics and performance metrics

## Development

### Project Structure

```
zscheduler/
├── run.py                  # Launcher script
├── README.md               # This file
├── requirements.txt        # Dependencies
├── zscheduler_app/         # Application package
│   ├── __init__.py
│   ├── main.py             # Main entry point
│   ├── config/             # Configuration components
│   │   ├── __init__.py
│   │   └── app_config.py
│   ├── data/               # Data persistence
│   │   ├── __init__.py
│   │   └── json_store.py
│   ├── scheduler/          # Scheduling components
│   │   ├── __init__.py
│   │   └── scheduler.py
│   ├── themes/             # UI themes
│   │   ├── __init__.py
│   │   └── theme_manager.py
│   └── ui/                 # User interface components
│       ├── __init__.py
│       ├── main_window.py
│       ├── icons.py
│       ├── schedule_list_view.py
│       ├── calendar_view.py
│       ├── timeline_view.py
│       ├── statistics_dashboard.py
│       ├── system_tray.py
│       └── dialogs/        # Various dialogs
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Future Plans

- More advanced scheduling options
- Plugin system for extending functionality
- Remote management capabilities
- Mobile companion app
- Enhanced statistics and reporting
