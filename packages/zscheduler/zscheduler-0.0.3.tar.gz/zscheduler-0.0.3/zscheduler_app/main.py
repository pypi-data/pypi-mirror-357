#!/usr/bin/env python3
"""
Main entry point for ZScheduler application
"""
import os
import sys
import logging
import argparse
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from zscheduler_app.config.app_config import AppConfig
from zscheduler_app.data.json_store import JsonStore
from zscheduler_app.scheduler.scheduler import Scheduler
from zscheduler_app.ui.main_window import MainWindow
from zscheduler_app.ui.icons import IconProvider


def setup_logging():
    """Configure logging for the application"""
    log_dir = Path.home() / ".zscheduler" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "zscheduler.log"

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File handler for detailed logging
    file_handler = logging.FileHandler(str(log_file))
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    # Console handler for important messages only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.info("Logging initialized. Log file: " + str(log_file))


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="ZScheduler - Task Scheduler")
    parser.add_argument("--reset-schedules", action="store_true",
                        help="Reset schedules file (delete all schedules)")
    return parser.parse_args()


def main():
    """
    Main application entry point
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Log platform information
    logger.info("Starting ZScheduler on " + sys.platform)

    # Get paths
    schedules_path = Path.home() / ".zscheduler" / "schedules.json"

    # Handle reset-schedules option
    if args.reset_schedules:
        logger.info(f"Resetting schedules file: {schedules_path}")
        json_store = JsonStore(schedules_path)
        if json_store.delete_file():
            logger.info("Schedules file reset successfully")
            print("Schedules file reset successfully")
            return 0
        else:
            logger.error("Failed to reset schedules file")
            print("Failed to reset schedules file")
            return 1

    # Initialize Qt application
    # High DPI settings are handled automatically in newer PyQt versions
    app = QApplication(sys.argv)
    app.setApplicationName("ZScheduler")
    app.setOrganizationName("ZScheduler")
    app.setOrganizationDomain("zscheduler.example.com")

    # Initialize icon provider
    icon_provider = IconProvider.get_instance()
    app.setWindowIcon(icon_provider.get_app_icon())

    try:
        # Load configuration
        config_path = Path.home() / ".zscheduler" / "config.json"
        logger.info("Loading configuration from " + str(config_path))
        app_config = AppConfig(config_path)

        # Initialize schedule store
        logger.info("Initializing schedule store at " + str(schedules_path))
        json_store = JsonStore(schedules_path)

        # Initialize scheduler
        logger.info("Initializing scheduler")
        scheduler = Scheduler()

        # Load schedules
        try:
            schedules = json_store.load()
            if schedules:
                for schedule in schedules:
                    scheduler.add_schedule(schedule)
                logger.info("Loaded " + str(len(schedules)) + " schedule(s)")
            else:
                logger.info("No saved schedules found")
        except Exception as e:
            logger.error("Error loading schedules: " + str(e))

        # Create and show main window
        logger.info("Creating main window")
        main_window = MainWindow(app_config, scheduler, json_store)
        main_window.show()

        # Auto-save schedules and cleanup when application exits
        def cleanup_and_save():
            try:
                # Stop the scheduler first
                logger.info("Stopping scheduler...")
                scheduler.stop()

                # Save schedules
                schedules = scheduler.get_schedules()
                json_store.save(schedules)
                logger.info("Saved " + str(len(schedules)) + " schedule(s)")
                logger.info("Application cleanup completed")
            except Exception as e:
                logger.error("Error during cleanup: " + str(e))

        app.aboutToQuit.connect(cleanup_and_save)

        # Start scheduler
        logger.info("Starting scheduler")
        scheduler.start()

        # Run application
        logger.info("Application started")
        return app.exec()

    except Exception as e:
        logger.critical("Unhandled application error: " + str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
