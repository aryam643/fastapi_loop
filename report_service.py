"""
Service layer for handling report generation requests
"""
import uuid
import threading
from datetime import datetime
from sqlalchemy.orm import Session
from models import ReportStatus
from report_generator import ReportGenerator
from database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportService:
    """Service for managing report generation"""
    
    @staticmethod
    def trigger_report() -> str:
        """Trigger a new report generation and return report_id"""
        report_id = str(uuid.uuid4())
        
        # Create report status record
        db: Session = SessionLocal()
        try:
            report_status = ReportStatus(
                report_id=report_id,
                status="Running",
                created_at=datetime.utcnow()
            )
            db.add(report_status)
            db.commit()
            
            # Start report generation in background thread
            thread = threading.Thread(
                target=ReportService._generate_report_background,
                args=(report_id,)
            )
            thread.daemon = True
            thread.start()
            
            logger.info(f"Report generation triggered with ID: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"Error triggering report: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    @staticmethod
    def _generate_report_background(report_id: str):
        """Background task to generate report"""
        db: Session = SessionLocal()
        try:
            generator = ReportGenerator(db)
            generator.generate_report_async(report_id)
        except Exception as e:
            logger.error(f"Background report generation failed for {report_id}: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def get_report_status(report_id: str) -> dict:
        """Get report status and file if complete"""
        db: Session = SessionLocal()
        try:
            report_status = db.query(ReportStatus).filter(ReportStatus.report_id == report_id).first()
            
            if not report_status:
                return {"error": "Report not found"}
            
            if report_status.status == "Complete":
                return {
                    "status": "Complete",
                    "file_path": report_status.file_path,
                    "completed_at": report_status.completed_at
                }
            else:
                return {
                    "status": report_status.status,
                    "created_at": report_status.created_at
                }
                
        except Exception as e:
            logger.error(f"Error getting report status: {str(e)}")
            return {"error": "Internal server error"}
        finally:
            db.close()
