import pandas as pd
import pytz
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from models import StoreStatus, BusinessHours, StoreTimezone, get_db
from business_hours_utils import business_hours_calc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data import and processing logic for store monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.business_calc = business_hours_calc
    
    def import_csv_data(self, store_status_path: str, business_hours_path: str, timezones_path: str):
        """Import data from CSV files into database"""
        try:
            logger.info("Clearing existing data...")
            self.db.query(StoreStatus).delete()
            self.db.query(BusinessHours).delete()
            self.db.query(StoreTimezone).delete()
            self.db.commit()
            
            # Import store status data
            logger.info("Importing store status data...")
            status_df = pd.read_csv(store_status_path)
            status_records = []
            for _, row in status_df.iterrows():
                store_status = StoreStatus(
                    store_id=str(row['store_id']),
                    timestamp_utc=pd.to_datetime(row['timestamp_utc']),
                    status=row['status']
                )
                status_records.append(store_status)
            
            self.db.add_all(status_records)
            logger.info(f"Imported {len(status_records)} store status records")
            
            # Import business hours data
            logger.info("Importing business hours data...")
            hours_df = pd.read_csv(business_hours_path)
            hours_records = []
            for _, row in hours_df.iterrows():
                business_hours = BusinessHours(
                    store_id=str(row['store_id']),
                    day_of_week=int(row['dayOfWeek']),
                    start_time_local=row['start_time_local'],
                    end_time_local=row['end_time_local']
                )
                hours_records.append(business_hours)
            
            self.db.add_all(hours_records)
            logger.info(f"Imported {len(hours_records)} business hours records")
            
            # Import timezone data
            logger.info("Importing timezone data...")
            tz_df = pd.read_csv(timezones_path)
            tz_records = []
            for _, row in tz_df.iterrows():
                store_tz = StoreTimezone(
                    store_id=str(row['store_id']),
                    timezone_str=row['timezone_str']
                )
                tz_records.append(store_tz)
            
            self.db.add_all(tz_records)
            logger.info(f"Imported {len(tz_records)} timezone records")
            
            self.db.commit()
            logger.info("Data import completed successfully")
            
        except Exception as e:
            logger.error(f"Error importing data: {str(e)}")
            self.db.rollback()
            raise
    
    def get_store_timezone(self, store_id: str) -> str:
        """Get timezone for a store, default to America/Chicago if not found"""
        store_tz = self.db.query(StoreTimezone).filter(StoreTimezone.store_id == store_id).first()
        timezone_str = store_tz.timezone_str if store_tz else "America/Chicago"
        
        return self.business_calc.validate_timezone(timezone_str)
    
    def get_business_hours(self, store_id: str) -> Dict[int, Tuple[time, time]]:
        """Get business hours for a store, default to 24/7 if not found"""
        hours = self.db.query(BusinessHours).filter(BusinessHours.store_id == store_id).all()
        
        if not hours:
            # Default to 24/7 operation
            return {i: (time(0, 0), time(23, 59, 59)) for i in range(7)}
        
        business_hours = {}
        for hour in hours:
            try:
                start_time = self.business_calc.parse_time_string(hour.start_time_local)
                end_time = self.business_calc.parse_time_string(hour.end_time_local)
                business_hours[hour.day_of_week] = (start_time, end_time)
            except ValueError as e:
                logger.error(f"Invalid time format for store {store_id}, day {hour.day_of_week}: {str(e)}")
                # Skip this day's business hours
                continue
        
        return business_hours
    
    def convert_utc_to_local(self, utc_timestamp: datetime, timezone_str: str) -> datetime:
        """Convert UTC timestamp to local timezone with enhanced error handling"""
        return self.business_calc.convert_utc_to_local_safe(utc_timestamp, timezone_str)
    
    def is_within_business_hours(self, local_timestamp: datetime, business_hours: Dict[int, Tuple[time, time]]) -> bool:
        """Check if a timestamp falls within business hours using enhanced logic"""
        return self.business_calc.is_within_business_hours_enhanced(local_timestamp, business_hours)
    
    def get_max_timestamp(self) -> datetime:
        """Get the maximum timestamp from store status data"""
        max_timestamp = self.db.query(StoreStatus.timestamp_utc).order_by(StoreStatus.timestamp_utc.desc()).first()
        return max_timestamp[0] if max_timestamp else datetime.utcnow()
    
    def get_all_store_ids(self) -> List[str]:
        """Get all unique store IDs from the database"""
        store_ids = self.db.query(StoreStatus.store_id).distinct().all()
        return [store_id[0] for store_id in store_ids]
    
    def get_store_status_in_range(self, store_id: str, start_time: datetime, end_time: datetime) -> List[StoreStatus]:
        """Get store status data for a specific store within a time range"""
        return self.db.query(StoreStatus).filter(
            StoreStatus.store_id == store_id,
            StoreStatus.timestamp_utc >= start_time,
            StoreStatus.timestamp_utc <= end_time
        ).order_by(StoreStatus.timestamp_utc).all()
