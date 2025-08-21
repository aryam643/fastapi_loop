"""
Test script for business hours and timezone logic
"""
from datetime import datetime, time
from business_hours_utils import BusinessHoursCalculator
import pytz

def test_business_hours_logic():
    """Test various business hours scenarios"""
    calc = BusinessHoursCalculator()
    
    print("Testing Business Hours Logic...")
    
    # Test 1: Normal business hours (9 AM to 5 PM)
    print("\n1. Testing normal business hours (9 AM to 5 PM):")
    business_hours = {
        0: (time(9, 0), time(17, 0)),  # Monday
        1: (time(9, 0), time(17, 0)),  # Tuesday
        2: (time(9, 0), time(17, 0)),  # Wednesday
        3: (time(9, 0), time(17, 0)),  # Thursday
        4: (time(9, 0), time(17, 0)),  # Friday
    }
    
    # Test during business hours
    test_time = datetime(2024, 1, 15, 14, 30)  # Monday 2:30 PM
    result = calc.is_within_business_hours_enhanced(test_time, business_hours)
    print(f"Monday 2:30 PM: {result} (should be True)")
    
    # Test outside business hours
    test_time = datetime(2024, 1, 15, 19, 30)  # Monday 7:30 PM
    result = calc.is_within_business_hours_enhanced(test_time, business_hours)
    print(f"Monday 7:30 PM: {result} (should be False)")
    
    # Test weekend
    test_time = datetime(2024, 1, 13, 14, 30)  # Saturday 2:30 PM
    result = calc.is_within_business_hours_enhanced(test_time, business_hours)
    print(f"Saturday 2:30 PM: {result} (should be False)")
    
    # Test 2: Overnight business hours (10 PM to 6 AM)
    print("\n2. Testing overnight business hours (10 PM to 6 AM):")
    overnight_hours = {
        0: (time(22, 0), time(6, 0)),  # Monday night to Tuesday morning
        1: (time(22, 0), time(6, 0)),  # Tuesday night to Wednesday morning
    }
    
    # Test during overnight hours - late night
    test_time = datetime(2024, 1, 15, 23, 30)  # Monday 11:30 PM
    result = calc.is_within_business_hours_enhanced(test_time, overnight_hours)
    print(f"Monday 11:30 PM: {result} (should be True)")
    
    # Test during overnight hours - early morning
    test_time = datetime(2024, 1, 16, 3, 30)  # Tuesday 3:30 AM
    result = calc.is_within_business_hours_enhanced(test_time, overnight_hours)
    print(f"Tuesday 3:30 AM: {result} (should be True)")
    
    # Test outside overnight hours
    test_time = datetime(2024, 1, 16, 8, 30)  # Tuesday 8:30 AM
    result = calc.is_within_business_hours_enhanced(test_time, overnight_hours)
    print(f"Tuesday 8:30 AM: {result} (should be False)")
    
    # Test 3: Business seconds calculation
    print("\n3. Testing business seconds calculation:")
    start_time = datetime(2024, 1, 15, 8, 0)  # Monday 8 AM
    end_time = datetime(2024, 1, 15, 18, 0)   # Monday 6 PM
    
    total_seconds = calc.calculate_total_business_seconds_precise(start_time, end_time, business_hours)
    total_hours = total_seconds / 3600
    print(f"Business hours between 8 AM and 6 PM on Monday: {total_hours} hours (should be 8.0)")
    
    # Test 4: Timezone conversion
    print("\n4. Testing timezone conversion:")
    utc_time = datetime(2024, 1, 15, 20, 0)  # 8 PM UTC
    
    # Convert to different timezones
    timezones = ["America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London"]
    
    for tz in timezones:
        local_time = calc.convert_utc_to_local_safe(utc_time, tz)
        print(f"UTC {utc_time} -> {tz}: {local_time}")
    
    # Test invalid timezone
    invalid_tz_time = calc.convert_utc_to_local_safe(utc_time, "Invalid/Timezone")
    print(f"Invalid timezone handling: {invalid_tz_time}")
    
    print("\nBusiness hours logic tests completed!")

if __name__ == "__main__":
    test_business_hours_logic()
