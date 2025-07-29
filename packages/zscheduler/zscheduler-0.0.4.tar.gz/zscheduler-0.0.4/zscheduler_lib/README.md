# ZScheduler Library

A high-performance, feature-rich Python task scheduling library.

## Features

- Schedule OS commands and Python functions/classes/modules
- One-time, recurring, and N-times schedules
- Flexible time specifications (absolute dates, relative times, cron expressions)
- Robust error handling and recovery mechanisms
- Clean, terse API designed for developer happiness

## Installation

```bash
pip install zscheduler
```

## Quick Start

```python
from zscheduler import Scheduler, Task

# Create a scheduler
scheduler = Scheduler()

# Schedule a simple function to run after 5 minutes
def hello_world():
    print("Hello, World!")

scheduler.schedule(hello_world).after(minutes=5)

# Schedule a system command to run daily at 3 AM
scheduler.schedule("backup.sh").daily_at("03:00")

# Schedule a function to run exactly 3 times, every hour
def process_data(batch_id):
    print(f"Processing batch {batch_id}")

scheduler.schedule(process_data, args=[42]).every(hours=1).repeat(3)

# Start the scheduler
scheduler.start()
```

## Documentation

For full documentation, visit [docs.zscheduler.example.com](https://docs.zscheduler.example.com)

## License

MIT
