"""
Report Generation Engine for Store Monitoring System
Handles complex uptime/downtime calculations with business hours and timezone logic
"""
import pandas as pd
import pytz
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from models import StoreStatus, ReportStatus
from data_processor import DataProcessor
from csv_export_utils import csv_exporter
import logging
import uuid
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates uptime/downtime reports for stores"""
    
    def __init__(self, db: Session):
        self.db = db
        self.processor = DataProcessor(db)
        self.csv_exporter = csv_exporter
    
    def generate_report_async(self, report_id: str) -> None:
        """Generate report asynchronously and save to CSV"""
        try:
            logger.info(f"Starting report generation for report_id: {report_id}")
            
            # Update report status to running
            report_status = self.db.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
            if not report_status:
                raise ValueError(f"Report {report_id} not found")
            
            # Get current timestamp (max timestamp from data as per requirements)
            current_time = self.processor.get_max_timestamp()
            logger.info(f"Using current time: {current_time}")
            
            # Calculate time ranges
            one_hour_ago = current_time - timedelta(hours=1)
            one_day_ago = current_time - timedelta(days=1)
            one_week_ago = current_time - timedelta(weeks=1)
            
            # Get all store IDs
            store_ids = self.processor.get_all_store_ids()
            logger.info(f"Processing {len(store_ids)} stores")
            
            # Generate report data
            report_data = []
            
            for i, store_id in enumerate(store_ids):
                if i % 100 == 0:  # Log progress every 100 stores
                    logger.info(f"Processing store {i+1}/{len(store_ids)}")
                
                try:
                    store_report = self._calculate_store_metrics(
                        store_id, current_time, one_hour_ago, one_day_ago, one_week_ago
                    )
                    report_data.append(store_report)
                except Exception as e:
                    logger.error(f"Error processing store {store_id}: {str(e)}")
                    # Add default values for failed stores
                    report_data.append({
                        'store_id': store_id,
                        'uptime_last_hour': 0,
                        'uptime_last_day': 0,
                        'uptime_last_week': 0,
                        'downtime_last_hour': 0,
                        'downtime_last_day': 0,
                        'downtime_last_week': 0
                    })
            
            csv_path = self.csv_exporter.export_to_csv(report_data, report_id, validate=True)
            
            # Update report status to complete
            report_status.status = "Complete"
            report_status.completed_at = datetime.utcnow()
            report_status.file_path = csv_path
            self.db.commit()
            
            logger.info(f"Report generation completed for report_id: {report_id}")
            
        except Exception as e:
            logger.error(f"Error generating report {report_id}: {str(e)}")
            # Update report status to failed
            report_status = self.db.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
            if report_status:
                report_status.status = "Failed"
                self.db.commit()
            raise
    
    def _calculate_store_metrics(self, store_id: str, current_time: datetime, 
                               one_hour_ago: datetime, one_day_ago: datetime, 
                               one_week_ago: datetime) -> Dict:
        """Calculate uptime/downtime metrics for a single store"""
        
        # Get store timezone and business hours
        timezone_str = self.processor.get_store_timezone(store_id)
        business_hours = self.processor.get_business_hours(store_id)
        
        # Calculate metrics for each time period
        hour_metrics = self._calculate_period_metrics(
            store_id, one_hour_ago, current_time, timezone_str, business_hours
        )
        
        day_metrics = self._calculate_period_metrics(
            store_id, one_day_ago, current_time, timezone_str, business_hours
        )
        
        week_metrics = self._calculate_period_metrics(
            store_id, one_week_ago, current_time, timezone_str, business_hours
        )
        
        return {
            'store_id': store_id,
            'uptime_last_hour': round(hour_metrics['uptime'] / 60, 2),  # Convert to minutes
            'uptime_last_day': round(day_metrics['uptime'] / 3600, 2),  # Convert to hours
            'uptime_last_week': round(week_metrics['uptime'] / 3600, 2),  # Convert to hours
            'downtime_last_hour': round(hour_metrics['downtime'] / 60, 2),  # Convert to minutes
            'downtime_last_day': round(day_metrics['downtime'] / 3600, 2),  # Convert to hours
            'downtime_last_week': round(week_metrics['downtime'] / 3600, 2)  # Convert to hours
        }
    
    def _calculate_period_metrics(self, store_id: str, start_time: datetime, 
                                end_time: datetime, timezone_str: str, 
                                business_hours: Dict[int, Tuple[time, time]]) -> Dict:
        """Calculate uptime/downtime for a specific time period"""
        
        # Get store status data for the period
        status_data = self.processor.get_store_status_in_range(store_id, start_time, end_time)
        
        if not status_data:
            # No data available, assume store was inactive
            total_business_seconds = self._calculate_total_business_seconds(
                start_time, end_time, timezone_str, business_hours
            )
            return {'uptime': 0, 'downtime': total_business_seconds}
        
        # Convert to local timezone and filter by business hours
        local_status_data = []
        for status in status_data:
            local_timestamp = self.processor.convert_utc_to_local(status.timestamp_utc, timezone_str)
            if self.processor.is_within_business_hours(local_timestamp, business_hours):
                local_status_data.append({
                    'timestamp': local_timestamp,
                    'status': status.status,
                    'utc_timestamp': status.timestamp_utc
                })
        
        if not local_status_data:
            # No business hours data available
            total_business_seconds = self._calculate_total_business_seconds(
                start_time, end_time, timezone_str, business_hours
            )
            return {'uptime': 0, 'downtime': total_business_seconds}
        
        # Sort by timestamp
        local_status_data.sort(key=lambda x: x['timestamp'])
        
        # Calculate uptime/downtime using interpolation
        return self._interpolate_uptime_downtime(
            local_status_data, start_time, end_time, timezone_str, business_hours
        )
    
    def _interpolate_uptime_downtime(self, status_data: List[Dict], start_time: datetime,
                                   end_time: datetime, timezone_str: str,
                                   business_hours: Dict[int, Tuple[time, time]]) -> Dict:
        """
        Interpolate uptime/downtime from sparse polling data
        
        Logic:
        1. For each pair of consecutive observations, assume the status remains constant
        2. Only count time within business hours
        3. Handle edge cases at the beginning and end of the period
        """
        
        total_uptime = 0
        total_downtime = 0
        
        # Convert start and end times to local timezone
        local_start = self.processor.convert_utc_to_local(start_time, timezone_str)
        local_end = self.processor.convert_utc_to_local(end_time, timezone_str)
        
        # Handle case with single observation
        if len(status_data) == 1:
            observation = status_data[0]
            # Calculate business hours between start and observation
            business_seconds_before = self._calculate_business_seconds_between(
                local_start, observation['timestamp'], business_hours
            )
            # Calculate business hours between observation and end
            business_seconds_after = self._calculate_business_seconds_between(
                observation['timestamp'], local_end, business_hours
            )
            
            if observation['status'] == 'active':
                total_uptime = business_seconds_before + business_seconds_after
            else:
                total_downtime = business_seconds_before + business_seconds_after
            
            return {'uptime': total_uptime, 'downtime': total_downtime}
        
        # Handle multiple observations
        for i in range(len(status_data)):
            current_obs = status_data[i]
            
            if i == 0:
                # First observation: extrapolate backwards to start_time
                period_start = local_start
                period_end = current_obs['timestamp']
            else:
                # Use previous observation's timestamp as start
                period_start = status_data[i-1]['timestamp']
                period_end = current_obs['timestamp']
            
            # Calculate business seconds in this period
            business_seconds = self._calculate_business_seconds_between(
                period_start, period_end, business_hours
            )
            
            # Use previous status (or assume inactive for first period)
            if i == 0:
                # For the first period, we don't know the status, so we use current observation
                # This is a simplification - in practice, you might want different logic
                status = current_obs['status']
            else:
                status = status_data[i-1]['status']
            
            if status == 'active':
                total_uptime += business_seconds
            else:
                total_downtime += business_seconds
        
        # Handle the period after the last observation
        if status_data:
            last_obs = status_data[-1]
            business_seconds = self._calculate_business_seconds_between(
                last_obs['timestamp'], local_end, business_hours
            )
            
            if last_obs['status'] == 'active':
                total_uptime += business_seconds
            else:
                total_downtime += business_seconds
        
        return {'uptime': total_uptime, 'downtime': total_downtime}
    
    def _calculate_business_seconds_between(self, start_time: datetime, end_time: datetime,
                                          business_hours: Dict[int, Tuple[time, time]]) -> int:
        """Calculate total business seconds between two timestamps"""
        if start_time >= end_time:
            return 0
        
        total_seconds = 0
        current_time = start_time
        
        while current_time < end_time:
            day_of_week = current_time.weekday()
            
            if day_of_week in business_hours:
                start_business, end_business = business_hours[day_of_week]
                
                # Get business hours for current day
                business_start = current_time.replace(
                    hour=start_business.hour,
                    minute=start_business.minute,
                    second=start_business.second,
                    microsecond=0
                )
                business_end = current_time.replace(
                    hour=end_business.hour,
                    minute=end_business.minute,
                    second=end_business.second,
                    microsecond=0
                )
                
                # Handle overnight business hours
                if start_business > end_business:
                    business_end += timedelta(days=1)
                
                # Calculate overlap with our time period
                period_start = max(current_time, business_start)
                period_end = min(end_time, business_end)
                
                if period_start < period_end:
                    total_seconds += (period_end - period_start).total_seconds()
            
            # Move to next day
            current_time = (current_time + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        
        return int(total_seconds)
    
    def _calculate_total_business_seconds(self, start_time: datetime, end_time: datetime,
                                        timezone_str: str, business_hours: Dict[int, Tuple[time, time]]) -> int:
        """Calculate total business seconds in a time period"""
        local_start = self.processor.convert_utc_to_local(start_time, timezone_str)
        local_end = self.processor.convert_utc_to_local(end_time, timezone_str)
        
        return self._calculate_business_seconds_between(local_start, local_end, business_hours)
