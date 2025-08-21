"""
Script to generate a sample CSV report for testing and demonstration
"""
from csv_export_utils import csv_exporter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Generate sample CSV reports"""
    print("Generating sample CSV reports...")
    
    try:
        # Generate a small sample report
        print("\n1. Generating small sample report (10 stores)...")
        small_csv = csv_exporter.generate_sample_csv(num_stores=10)
        print(f"Small sample report generated: {small_csv}")
        
        # Generate a larger sample report
        print("\n2. Generating larger sample report (100 stores)...")
        large_csv = csv_exporter.generate_sample_csv(num_stores=100)
        print(f"Large sample report generated: {large_csv}")
        
        # Get statistics for the reports
        print("\n3. Getting statistics for the large report...")
        stats = csv_exporter.get_csv_stats(large_csv)
        
        if "error" not in stats:
            print(f"Total stores: {stats['total_stores']}")
            print(f"Average uptime (week): {stats['averages']['uptime_last_week']} hours")
            print(f"Best performing store: {stats['best_performing_store']['store_id']} "
                  f"({stats['best_performing_store']['uptime_last_week']} hours)")
            print(f"Worst performing store: {stats['worst_performing_store']['store_id']} "
                  f"({stats['worst_performing_store']['uptime_last_week']} hours)")
        else:
            print(f"Error getting stats: {stats['error']}")
        
        # Test CSV validation
        print("\n4. Testing CSV validation...")
        try:
            data = csv_exporter.read_and_validate_csv(large_csv)
            print(f"CSV validation successful! Read {len(data)} records.")
        except Exception as e:
            print(f"CSV validation failed: {str(e)}")
        
        print("\nSample report generation completed!")
        
    except Exception as e:
        logger.error(f"Error generating sample reports: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
