#!/usr/bin/env python3
"""
Development runner for ISKCON-Broadcast

This script runs the application with mock cameras for development
without requiring actual camera hardware.
"""

import sys
import os
import shutil
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_dev_environment():
    """Setup development environment by copying dev config"""
    
    # Backup original config if it exists
    if os.path.exists('mode_config.yaml'):
        if not os.path.exists('mode_config_production.yaml'):
            shutil.copy('mode_config.yaml', 'mode_config_production.yaml')
            logger.info("Backed up production config to mode_config_production.yaml")
    
    # Copy dev config to main config
    if os.path.exists('mode_config_dev.yaml'):
        shutil.copy('mode_config_dev.yaml', 'mode_config.yaml')
        logger.info("Using development configuration (mock cameras)")
    else:
        logger.error("Development config file not found: mode_config_dev.yaml")
        return False
    
    return True


def restore_production_environment():
    """Restore production environment"""
    
    if os.path.exists('mode_config_production.yaml'):
        shutil.copy('mode_config_production.yaml', 'mode_config.yaml')
        logger.info("Restored production configuration")
    else:
        logger.warning("No production config backup found")


def run_application(debug_time=None):
    """Run the main application"""
    
    try:
        # Import and run the main application
        import video_stream
        import asyncio
        from datetime import datetime
        
        if debug_time:
            try:
                debug_time = datetime.strptime(debug_time, "%H:%M").time()
                logger.info(f"Debug mode activated. Testing schedule at {debug_time}.")
            except ValueError:
                logger.error("Invalid time format for debug-time. Please use HH:MM.")
                return False
        
        logger.info("Starting ISKCON-Broadcast with mock cameras...")
        asyncio.run(video_stream.main(debug_time))
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        return False
    
    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run ISKCON-Broadcast in development mode with mock cameras')
    parser.add_argument('--debug-time', type=str, help="Specify a debug time in HH:MM format for testing")
    parser.add_argument('--restore-production', action='store_true', help="Restore production configuration and exit")
    parser.add_argument('--test-only', action='store_true', help="Only test camera system, don't run main app")
    
    args = parser.parse_args()
    
    if args.restore_production:
        restore_production_environment()
        logger.info("Production configuration restored. Exiting.")
        return 0
    
    # Setup development environment
    if not setup_dev_environment():
        return 1
    
    try:
        if args.test_only:
            # Run camera tests only
            logger.info("Running camera system tests...")
            import test_cameras
            return test_cameras.main()
        else:
            # Run the full application
            success = run_application(args.debug_time)
            return 0 if success else 1
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    finally:
        # Cleanup - restore production config
        restore_production_environment()


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 