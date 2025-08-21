"""
Enhanced Business Hours and Timezone Utilities
Handles complex business hours calculations with robust timezone support
"""
import pytz
from datetime import datetime, time, timedelta
from typing import Dict, Tuple, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessHoursCalculator:
    """Enhanced calculator for business hours with timezone support"""
    
    def __init__(self):
        self.default_timezone = "America/Chicago"
        self.valid_timezones = set(pytz.all_timezones)
    
    def validate_timezone(self, timezone_str: str) -> str:
        """Validate and return a safe timezone string"""
        if timezone_str in self.valid_timezones:
            return timezone_str
        
        logger.warning(f"Invalid timezone '{timezone_str}', using default: {self.default_timezone}")
        return self.default_timezone
    
    def parse_time_string(self, time_str: str) -> time:
        """Parse time string in HH:MM:SS format with error handling"""
        try:
            return datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            try:
                # Try HH:MM format
                return datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                logger.error(f"Invalid time format: {time_str}")
                raise ValueError(f"Invalid time format: {time_str}")
    
    def convert_utc_to_local_safe(self, utc_timestamp: datetime, timezone_str: str) -> datetime:
        """Safely convert UTC timestamp to local timezone with DST handling"""
        try:
            # Validate timezone
            timezone_str = self.validate_timezone(timezone_str)
            
            utc_tz = pytz.UTC
            local_tz = pytz.timezone(timezone_str)
            
            # Ensure UTC timestamp is timezone-aware
            if utc_timestamp.tzinfo is None:
                utc_timestamp = utc_tz.localize(utc_timestamp)
            elif utc_timestamp.tzinfo != utc_tz:
                utc_timestamp = utc_timestamp.astimezone(utc_tz)
            
            # Convert to local timezone (handles DST automatically)
            local_timestamp = utc_timestamp.astimezone(local_tz)
            
            return local_timestamp
            
        except Exception as e:
            logger.error(f"Error converting timezone: {str(e)}")
            # Fallback: return UTC timestamp
            return utc_timestamp
    
    def is_within_business_hours_enhanced(self, local_timestamp: datetime, 
                                        business_hours: Dict[int, Tuple[time, time]]) -> bool:
        """
        Enhanced business hours check with better overnight handling
        
        Args:
            local_timestamp: Local datetime to check
            business_hours: Dict mapping day_of_week to (start_time, end_time)
        
        Returns:
            True if timestamp is within business hours
        """
        day_of_week = local_timestamp.weekday()  # 0=Monday, 6=Sunday
        current_time = local_timestamp.time()
        
        # Check current day's business hours
        if day_of_week in business_hours:
            start_time, end_time = business_hours[day_of_week]
            
            if start_time <= end_time:
                # Normal business hours (e.g., 9:00 to 17:00)
                if start_time <= current_time <= end_time:
                    return True
            else:
                # Overnight business hours (e.g., 22:00 to 06:00)
                if current_time >= start_time or current_time <= end_time:
                    return True
        
        # Check if this time falls within previous day's overnight hours
        prev_day = (day_of_week - 1) % 7
        if prev_day in business_hours:
            prev_start, prev_end = business_hours[prev_day]
            
            # If previous day has overnight hours and current time is before end time
            if prev_start > prev_end and current_time <= prev_end:
                return True
        
        return False
    
    def calculate_business_seconds_in_day(self, date: datetime, 
                                        business_hours: Dict[int, Tuple[time, time]]) -> int:
        """Calculate total business seconds in a specific day"""
        day_of_week = date.weekday()
        
        if day_of_week not in business_hours:
            return 0
        
        start_time, end_time = business_hours[day_of_week]
        
        if start_time <= end_time:
            # Normal business hours
            start_datetime = date.replace(
                hour=start_time.hour, 
                minute=start_time.minute, 
                second=start_time.second,
                microsecond=0
            )
            end_datetime = date.replace(
                hour=end_time.hour, 
                minute=end_time.minute, 
                second=end_time.second,
                microsecond=0
            )
            
            return int((end_datetime - start_datetime).total_seconds())
        else:
            # Overnight business hours - split into two parts
            # Part 1: From start_time to midnight
            start_datetime = date.replace(
                hour=start_time.hour, 
                minute=start_time.minute, 
                second=start_time.second,
                microsecond=0
            )
            midnight = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            part1_seconds = int((midnight - start_datetime).total_seconds()) + 1
            
            # Part 2: From midnight to end_time (next day)
            next_day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_datetime = date.replace(
                hour=end_time.hour, 
                minute=end_time.minute, 
                second=end_time.second,
                microsecond=0
            )
            part2_seconds = int((end_datetime - next_day_start).total_seconds())
            
            return part1_seconds + part2_seconds
    
    def get_business_hours_intervals(self, start_date: datetime, end_date: datetime,
                                   business_hours: Dict[int, Tuple[time, time]]) -> List[Tuple[datetime, datetime]]:
        """
        Get list of business hours intervals between two dates
        Useful for precise uptime/downtime calculations
        """
        intervals = []
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            
            if day_of_week in business_hours:
                start_time, end_time = business_hours[day_of_week]
                
                # Create business hours interval for this day
                interval_start = current_date.replace(
                    hour=start_time.hour,
                    minute=start_time.minute,
                    second=start_time.second,
                    microsecond=0
                )
                
                if start_time <= end_time:
                    # Normal business hours
                    interval_end = current_date.replace(
                        hour=end_time.hour,
                        minute=end_time.minute,
                        second=end_time.second,
                        microsecond=0
                    )
                    
                    # Clip to our date range
                    interval_start = max(interval_start, start_date)
                    interval_end = min(interval_end, end_date)
                    
                    if interval_start < interval_end:
                        intervals.append((interval_start, interval_end))
                        
                else:
                    # Overnight business hours - create two intervals
                    # Interval 1: start_time to midnight
                    midnight = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    interval_start_1 = max(interval_start, start_date)
                    interval_end_1 = min(midnight, end_date)
                    
                    if interval_start_1 < interval_end_1:
                        intervals.append((interval_start_1, interval_end_1))
                    
                    # Interval 2: midnight to end_time (next day)
                    next_day = current_date + timedelta(days=1)
                    interval_start_2 = max(next_day.replace(hour=0, minute=0, second=0, microsecond=0), start_date)
                    interval_end_2 = min(next_day.replace(
                        hour=end_time.hour,
                        minute=end_time.minute,
                        second=end_time.second,
                        microsecond=0
                    ), end_date)
                    
                    if interval_start_2 < interval_end_2:
                        intervals.append((interval_start_2, interval_end_2))
            
            current_date += timedelta(days=1)
        
        return intervals
    
    def calculate_total_business_seconds_precise(self, start_time: datetime, end_time: datetime,
                                               business_hours: Dict[int, Tuple[time, time]]) -> int:
        """
        Precisely calculate business seconds using interval-based approach
        More accurate than the day-by-day approach for edge cases
        """
        if start_time >= end_time:
            return 0
        
        intervals = self.get_business_hours_intervals(start_time, end_time, business_hours)
        total_seconds = 0
        
        for interval_start, interval_end in intervals:
            total_seconds += int((interval_end - interval_start).total_seconds())
        
        return total_seconds

# Global instance for easy access
business_hours_calc = BusinessHoursCalculator()
