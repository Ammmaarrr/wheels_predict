#!/usr/bin/env python3
"""
Automated Scraping and Cleaning Pipeline for PakWheels
=====================================================

This module provides automated pipelines for:
1. Scraping PakWheels listings
2. Cleaning and preprocessing data
3. Scheduling and monitoring
4. Error handling and recovery
"""

import os
import sys
import time
import json
import logging
import schedule
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import existing modules
try:
    from integrations.pakwheels_scraper import scrape_pakwheels_listings
    from data_processing.clean_and_preprocess import clean_data, get_latest_raw_csv
    from utils.logger import setup_logger
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    # We'll create fallback functions

class PipelineConfig:
    """Configuration for the automated pipeline"""
    
    def __init__(self, config_file: str = "config/pipeline_config.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "scraping": {
                "enabled": True,
                "schedule": "daily",
                "time": "02:00",
                "max_pages": 100,
                "retry_attempts": 3,
                "delay_between_requests": 2
            },
            "cleaning": {
                "enabled": True,
                "auto_clean_after_scrape": True,
                "backup_raw_data": True,
                "validation_checks": True
            },
            "monitoring": {
                "enabled": True,
                "log_level": "INFO",
                "email_notifications": False,
                "email_recipients": [],
                "webhook_url": ""
            },
            "storage": {
                "raw_data_dir": "data/raw",
                "cleaned_data_dir": "data/cleaned",
                "logs_dir": "logs",
                "max_raw_files": 10,
                "max_cleaned_files": 5
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                self.config = {**default_config, **user_config}
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = default_config
    
    def save_config(self):
        """Save configuration to JSON file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

class PipelineMonitor:
    """Monitor and track pipeline execution"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.db_path = "logs/pipeline_history.db"
        self._init_db()
    
    def _setup_logger(self):
        """Setup logging for pipeline"""
        log_dir = self.config.get('storage.logs_dir', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logger = logging.getLogger('pipeline')
        logger.setLevel(getattr(logging, self.config.get('monitoring.log_level', 'INFO')))
        
        # File handler
        file_handler = logging.FileHandler(f"{log_dir}/pipeline.log")
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(console_handler)
        
        return logger
    
    def _init_db(self):
        """Initialize SQLite database for tracking pipeline history"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    operation TEXT NOT NULL,
                    status TEXT NOT NULL,
                    records_processed INTEGER,
                    duration_seconds REAL,
                    error_message TEXT,
                    metadata TEXT
                )
            ''')
    
    def log_run(self, operation: str, status: str, records_processed: int = 0, 
                duration: float = 0, error_message: str = None, metadata: Dict = None):
        """Log a pipeline run to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO pipeline_runs 
                (operation, status, records_processed, duration_seconds, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (operation, status, records_processed, duration, error_message, 
                  json.dumps(metadata) if metadata else None))
        
        # Log to file
        if status == 'success':
            self.logger.info(f"{operation} completed successfully. "
                           f"Records: {records_processed}, Duration: {duration:.2f}s")
        else:
            self.logger.error(f"{operation} failed: {error_message}")
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent pipeline runs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM pipeline_runs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def send_notification(self, subject: str, message: str, is_error: bool = False):
        """Send notification (email or webhook)"""
        if not self.config.get('monitoring.enabled', True):
            return
        
        # Email notification
        if self.config.get('monitoring.email_notifications', False):
            recipients = self.config.get('monitoring.email_recipients', [])
            if recipients:
                self._send_email(subject, message, recipients)
        
        # Webhook notification
        webhook_url = self.config.get('monitoring.webhook_url', '')
        if webhook_url:
            self._send_webhook(subject, message, webhook_url, is_error)
    
    def _send_email(self, subject: str, message: str, recipients: List[str]):
        """Send email notification"""
        try:
            # This is a placeholder - you'd need to configure SMTP settings
            self.logger.info(f"Would send email to {recipients}: {subject}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
    
    def _send_webhook(self, subject: str, message: str, webhook_url: str, is_error: bool):
        """Send webhook notification"""
        try:
            import requests
            payload = {
                'subject': subject,
                'message': message,
                'is_error': is_error,
                'timestamp': datetime.now().isoformat()
            }
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")

class ScrapingPipeline:
    """Automated scraping pipeline"""
    
    def __init__(self, config: PipelineConfig, monitor: PipelineMonitor):
        self.config = config
        self.monitor = monitor
    
    def run_scraping(self) -> Tuple[bool, Dict]:
        """Run the scraping pipeline"""
        start_time = time.time()
        operation = "scraping"
        
        try:
            self.monitor.logger.info("Starting scraping pipeline...")
            
            # Create output directory
            raw_dir = self.config.get('storage.raw_data_dir', 'data/raw')
            os.makedirs(raw_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{raw_dir}/pakwheels_listings_{timestamp}.csv"
            
            # Run scraping
            if hasattr(sys.modules.get('integrations.pakwheels_scraper'), 'scrape_pakwheels_listings'):
                data = scrape_pakwheels_listings()
                
                if data and len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(output_file, index=False)
                    records_count = len(df)
                else:
                    raise Exception("No data scraped")
            else:
                # Fallback mock scraping for testing
                records_count = self._mock_scraping(output_file)
            
            duration = time.time() - start_time
            
            # Log success
            metadata = {
                'output_file': output_file,
                'timestamp': timestamp
            }
            self.monitor.log_run(operation, 'success', records_count, duration, None, metadata)
            
            # Clean up old files
            self._cleanup_old_files(raw_dir, self.config.get('storage.max_raw_files', 10))
            
            return True, {'records_count': records_count, 'output_file': output_file}
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            self.monitor.log_run(operation, 'failed', 0, duration, error_msg)
            self.monitor.send_notification(
                "Scraping Pipeline Failed",
                f"Error: {error_msg}\nDuration: {duration:.2f}s",
                is_error=True
            )
            
            return False, {'error': error_msg}
    
    def _mock_scraping(self, output_file: str) -> int:
        """Mock scraping for testing purposes"""
        self.monitor.logger.info("Running mock scraping (for testing)")
        
        # Create sample data
        sample_data = []
        for i in range(50):
            sample_data.append({
                'title': f'Toyota Corolla {2015 + i % 8}',
                'price': f'Rs {1500000 + i * 50000}',
                'year': 2015 + i % 8,
                'mileage': f'{30000 + i * 1000} km',
                'location': 'Karachi' if i % 2 == 0 else 'Lahore',
                'scraped_at': datetime.now().isoformat()
            })
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_file, index=False)
        
        return len(df)
    
    def _cleanup_old_files(self, directory: str, max_files: int):
        """Remove old files to keep only the most recent ones"""
        try:
            files = [f for f in os.listdir(directory) if f.endswith('.csv')]
            files.sort(reverse=True)  # Most recent first
            
            if len(files) > max_files:
                files_to_remove = files[max_files:]
                for file in files_to_remove:
                    os.remove(os.path.join(directory, file))
                    self.monitor.logger.info(f"Removed old file: {file}")
        except Exception as e:
            self.monitor.logger.error(f"Error cleaning up old files: {e}")

class CleaningPipeline:
    """Automated data cleaning pipeline"""
    
    def __init__(self, config: PipelineConfig, monitor: PipelineMonitor):
        self.config = config
        self.monitor = monitor
    
    def run_cleaning(self, input_file: str = None) -> Tuple[bool, Dict]:
        """Run the data cleaning pipeline"""
        start_time = time.time()
        operation = "cleaning"
        
        try:
            self.monitor.logger.info("Starting cleaning pipeline...")
            
            # Determine input file
            if input_file is None:
                raw_dir = self.config.get('storage.raw_data_dir', 'data/raw')
                if hasattr(sys.modules.get('data_processing.clean_and_preprocess'), 'get_latest_raw_csv'):
                    input_file = get_latest_raw_csv()
                else:
                    # Fallback to find latest file
                    files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
                    if not files:
                        raise FileNotFoundError("No raw CSV files found")
                    files.sort(reverse=True)
                    input_file = os.path.join(raw_dir, files[0])
            
            # Create output directory
            cleaned_dir = self.config.get('storage.cleaned_data_dir', 'data/cleaned')
            os.makedirs(cleaned_dir, exist_ok=True)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{cleaned_dir}/pakwheels_listings_cleaned_{timestamp}.csv"
            
            # Run cleaning
            if hasattr(sys.modules.get('data_processing.clean_and_preprocess'), 'clean_data'):
                clean_data(input_file, output_file)
            else:
                # Fallback basic cleaning
                self._basic_cleaning(input_file, output_file)
            
            # Get record count
            df = pd.read_csv(output_file)
            records_count = len(df)
            
            duration = time.time() - start_time
            
            # Log success
            metadata = {
                'input_file': input_file,
                'output_file': output_file,
                'timestamp': timestamp
            }
            self.monitor.log_run(operation, 'success', records_count, duration, None, metadata)
            
            # Clean up old files
            self._cleanup_old_files(cleaned_dir, self.config.get('storage.max_cleaned_files', 5))
            
            return True, {'records_count': records_count, 'output_file': output_file}
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            self.monitor.log_run(operation, 'failed', 0, duration, error_msg)
            self.monitor.send_notification(
                "Cleaning Pipeline Failed",
                f"Error: {error_msg}\nDuration: {duration:.2f}s",
                is_error=True
            )
            
            return False, {'error': error_msg}
    
    def _basic_cleaning(self, input_file: str, output_file: str):
        """Basic data cleaning fallback"""
        self.monitor.logger.info("Running basic data cleaning")
        
        df = pd.read_csv(input_file)
        
        # Basic cleaning operations
        df = df.dropna(axis=1, how='all')  # Remove empty columns
        df = df.drop_duplicates()  # Remove duplicates
        df = df.fillna("")  # Fill NaN values
        
        # Save cleaned data
        df.to_csv(output_file, index=False)
        
        self.monitor.logger.info(f"Cleaned data saved to: {output_file}")
    
    def _cleanup_old_files(self, directory: str, max_files: int):
        """Remove old files to keep only the most recent ones"""
        try:
            files = [f for f in os.listdir(directory) if f.endswith('.csv')]
            files.sort(reverse=True)  # Most recent first
            
            if len(files) > max_files:
                files_to_remove = files[max_files:]
                for file in files_to_remove:
                    os.remove(os.path.join(directory, file))
                    self.monitor.logger.info(f"Removed old file: {file}")
        except Exception as e:
            self.monitor.logger.error(f"Error cleaning up old files: {e}")

class AutomatedPipeline:
    """Main automated pipeline orchestrator"""
    
    def __init__(self, config_file: str = "config/pipeline_config.json"):
        self.config = PipelineConfig(config_file)
        self.monitor = PipelineMonitor(self.config)
        self.scraping_pipeline = ScrapingPipeline(self.config, self.monitor)
        self.cleaning_pipeline = CleaningPipeline(self.config, self.monitor)
        self.is_running = False
    
    def run_full_pipeline(self):
        """Run the complete pipeline (scraping + cleaning)"""
        self.monitor.logger.info("Starting full automated pipeline...")
        
        # Run scraping
        if self.config.get('scraping.enabled', True):
            success, result = self.scraping_pipeline.run_scraping()
            
            if success and self.config.get('cleaning.auto_clean_after_scrape', True):
                # Run cleaning on the scraped data
                if self.config.get('cleaning.enabled', True):
                    input_file = result.get('output_file')
                    success, result = self.cleaning_pipeline.run_cleaning(input_file)
            
            if success:
                self.monitor.send_notification(
                    "Pipeline Completed Successfully",
                    f"Processed {result.get('records_count', 0)} records"
                )
        
        else:
            self.monitor.logger.info("Scraping is disabled in configuration")
    
    def run_cleaning_only(self):
        """Run only the cleaning pipeline"""
        if self.config.get('cleaning.enabled', True):
            self.cleaning_pipeline.run_cleaning()
        else:
            self.monitor.logger.info("Cleaning is disabled in configuration")
    
    def setup_scheduling(self):
        """Setup scheduled execution"""
        if not self.config.get('scraping.enabled', True):
            self.monitor.logger.info("Scheduling disabled - scraping is not enabled")
            return
        
        schedule_type = self.config.get('scraping.schedule', 'daily')
        schedule_time = self.config.get('scraping.time', '02:00')
        
        if schedule_type == 'daily':
            schedule.every().day.at(schedule_time).do(self.run_full_pipeline)
        elif schedule_type == 'weekly':
            schedule.every().sunday.at(schedule_time).do(self.run_full_pipeline)
        elif schedule_type == 'hourly':
            schedule.every().hour.do(self.run_full_pipeline)
        
        self.monitor.logger.info(f"Scheduled pipeline to run {schedule_type} at {schedule_time}")
    
    def start_scheduler(self):
        """Start the scheduler (blocking)"""
        self.setup_scheduling()
        self.is_running = True
        
        self.monitor.logger.info("Pipeline scheduler started. Press Ctrl+C to stop.")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.monitor.logger.info("Pipeline scheduler stopped by user")
        finally:
            self.is_running = False
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        self.monitor.logger.info("Pipeline scheduler stopped")
    
    def get_status(self) -> Dict:
        """Get pipeline status and recent runs"""
        recent_runs = self.monitor.get_recent_runs(5)
        
        return {
            'is_running': self.is_running,
            'config': self.config.config,
            'recent_runs': recent_runs,
            'next_run': str(schedule.next_run()) if schedule.jobs else None
        }

# CLI Interface
def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PakWheels Automated Pipeline')
    parser.add_argument('--config', default='config/pipeline_config.json', 
                       help='Configuration file path')
    parser.add_argument('--action', choices=['run', 'schedule', 'clean', 'status'], 
                       default='run', help='Action to perform')
    parser.add_argument('--setup', action='store_true', 
                       help='Setup initial configuration')
    
    args = parser.parse_args()
    
    if args.setup:
        # Create initial configuration
        config = PipelineConfig(args.config)
        config.save_config()
        print(f"Configuration created at: {args.config}")
        return
    
    # Create pipeline
    pipeline = AutomatedPipeline(args.config)
    
    if args.action == 'run':
        pipeline.run_full_pipeline()
    elif args.action == 'schedule':
        pipeline.start_scheduler()
    elif args.action == 'clean':
        pipeline.run_cleaning_only()
    elif args.action == 'status':
        status = pipeline.get_status()
        print(json.dumps(status, indent=2, default=str))

if __name__ == "__main__":
    main()
