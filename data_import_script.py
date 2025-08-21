"""
Script to import CSV data into the database
Run this script to populate the database with the provided CSV files
"""
import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, init_database
from data_processor import DataProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to import CSV data"""
    # Initialize database
    init_database()
    
    # CSV file paths (adjust these paths based on your data location)
    csv_files = {
        'store_status': 'data/store_status.csv',
        'business_hours': 'data/menu_hours.csv', 
        'timezones': 'data/timezones.csv'
    }
    
    # Check if CSV files exist
    for file_type, file_path in csv_files.items():
        if not os.path.exists(file_path):
            logger.error(f"CSV file not found: {file_path}")
            logger.info("Please ensure CSV files are placed in the 'data' directory")
            return
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Initialize data processor
        processor = DataProcessor(db)
        
        # Import data from CSV files
        logger.info("Starting data import process...")
        processor.import_csv_data(
            store_status_path=csv_files['store_status'],
            business_hours_path=csv_files['business_hours'],
            timezones_path=csv_files['timezones']
        )
        
        logger.info("Data import completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data import: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
