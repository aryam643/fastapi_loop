"""
Enhanced CSV Export Utilities for Store Monitoring Reports
Provides robust CSV generation, validation, and formatting capabilities
"""
import csv
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVExporter:
    """Enhanced CSV export functionality with validation and formatting"""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Define the expected schema for store monitoring reports
        self.report_schema = [
            'store_id',
            'uptime_last_hour',
            'uptime_last_day', 
            'uptime_last_week',
            'downtime_last_hour',
            'downtime_last_day',
            'downtime_last_week'
        ]
    
    def validate_report_data(self, report_data: List[Dict[str, Any]]) -> bool:
        """Validate report data against expected schema"""
        if not report_data:
            logger.error("Report data is empty")
            return False
        
        # Check if all required fields are present
        for i, record in enumerate(report_data):
            missing_fields = []
            for field in self.report_schema:
                if field not in record:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error(f"Record {i} missing fields: {missing_fields}")
                return False
            
            # Validate data types
            if not isinstance(record['store_id'], str):
                logger.error(f"Record {i}: store_id must be string")
                return False
            
            # Validate numeric fields
            numeric_fields = [f for f in self.report_schema if f != 'store_id']
            for field in numeric_fields:
                try:
                    float(record[field])
                except (ValueError, TypeError):
                    logger.error(f"Record {i}: {field} must be numeric")
                    return False
        
        return True
    
    def format_report_data(self, report_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format report data for consistent CSV output"""
        formatted_data = []
        
        for record in report_data:
            formatted_record = {
                'store_id': str(record['store_id']),
                'uptime_last_hour': round(float(record['uptime_last_hour']), 2),
                'uptime_last_day': round(float(record['uptime_last_day']), 2),
                'uptime_last_week': round(float(record['uptime_last_week']), 2),
                'downtime_last_hour': round(float(record['downtime_last_hour']), 2),
                'downtime_last_day': round(float(record['downtime_last_day']), 2),
                'downtime_last_week': round(float(record['downtime_last_week']), 2)
            }
            formatted_data.append(formatted_record)
        
        return formatted_data
    
    def export_to_csv(self, report_data: List[Dict[str, Any]], report_id: str, 
                     validate: bool = True) -> str:
        """
        Export report data to CSV file with validation and formatting
        
        Args:
            report_data: List of dictionaries containing report data
            report_id: Unique identifier for the report
            validate: Whether to validate data before export
            
        Returns:
            Path to the generated CSV file
        """
        try:
            # Validate data if requested
            if validate and not self.validate_report_data(report_data):
                raise ValueError("Report data validation failed")
            
            # Format data for consistent output
            formatted_data = self.format_report_data(report_data)
            
            # Sort by store_id for consistent output
            formatted_data.sort(key=lambda x: x['store_id'])
            
            # Generate CSV file path
            csv_filename = f"report_{report_id}.csv"
            csv_path = self.reports_dir / csv_filename
            
            # Write to CSV file
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.report_schema)
                writer.writeheader()
                writer.writerows(formatted_data)
            
            logger.info(f"CSV report exported successfully: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            raise
    
    def generate_sample_csv(self, num_stores: int = 10) -> str:
        """Generate a sample CSV file for testing purposes"""
        import random
        
        sample_data = []
        for i in range(num_stores):
            # Generate realistic sample data
            uptime_hour = round(random.uniform(45, 60), 2)  # 45-60 minutes
            downtime_hour = round(60 - uptime_hour, 2)
            
            uptime_day = round(random.uniform(18, 24), 2)  # 18-24 hours
            downtime_day = round(24 - uptime_day, 2)
            
            uptime_week = round(random.uniform(120, 168), 2)  # 120-168 hours
            downtime_week = round(168 - uptime_week, 2)
            
            sample_data.append({
                'store_id': f"store_{i+1:04d}",
                'uptime_last_hour': uptime_hour,
                'uptime_last_day': uptime_day,
                'uptime_last_week': uptime_week,
                'downtime_last_hour': downtime_hour,
                'downtime_last_day': downtime_day,
                'downtime_last_week': downtime_week
            })
        
        sample_report_id = f"sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        csv_path = self.export_to_csv(sample_data, sample_report_id)
        
        logger.info(f"Sample CSV generated: {csv_path}")
        return csv_path
    
    def read_and_validate_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Read and validate an existing CSV file"""
        try:
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
            # Read CSV file
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = list(reader)
            
            # Validate the data
            if not self.validate_report_data(data):
                raise ValueError("CSV data validation failed")
            
            logger.info(f"CSV file read and validated successfully: {csv_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            raise
    
    def get_csv_stats(self, csv_path: str) -> Dict[str, Any]:
        """Get statistics about a CSV report file"""
        try:
            data = self.read_and_validate_csv(csv_path)
            
            if not data:
                return {"error": "No data in CSV file"}
            
            # Calculate statistics
            total_stores = len(data)
            
            # Calculate averages
            avg_uptime_hour = sum(float(record['uptime_last_hour']) for record in data) / total_stores
            avg_uptime_day = sum(float(record['uptime_last_day']) for record in data) / total_stores
            avg_uptime_week = sum(float(record['uptime_last_week']) for record in data) / total_stores
            
            avg_downtime_hour = sum(float(record['downtime_last_hour']) for record in data) / total_stores
            avg_downtime_day = sum(float(record['downtime_last_day']) for record in data) / total_stores
            avg_downtime_week = sum(float(record['downtime_last_week']) for record in data) / total_stores
            
            # Find stores with highest/lowest uptime
            best_store_week = max(data, key=lambda x: float(x['uptime_last_week']))
            worst_store_week = min(data, key=lambda x: float(x['uptime_last_week']))
            
            stats = {
                "total_stores": total_stores,
                "averages": {
                    "uptime_last_hour": round(avg_uptime_hour, 2),
                    "uptime_last_day": round(avg_uptime_day, 2),
                    "uptime_last_week": round(avg_uptime_week, 2),
                    "downtime_last_hour": round(avg_downtime_hour, 2),
                    "downtime_last_day": round(avg_downtime_day, 2),
                    "downtime_last_week": round(avg_downtime_week, 2)
                },
                "best_performing_store": {
                    "store_id": best_store_week['store_id'],
                    "uptime_last_week": float(best_store_week['uptime_last_week'])
                },
                "worst_performing_store": {
                    "store_id": worst_store_week['store_id'],
                    "uptime_last_week": float(worst_store_week['uptime_last_week'])
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating CSV stats: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_old_reports(self, days_old: int = 7) -> int:
        """Clean up CSV reports older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            deleted_count = 0
            
            for csv_file in self.reports_dir.glob("report_*.csv"):
                if csv_file.stat().st_mtime < cutoff_time:
                    csv_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old report: {csv_file}")
            
            logger.info(f"Cleaned up {deleted_count} old report files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {str(e)}")
            return 0

# Global instance for easy access
csv_exporter = CSVExporter()
