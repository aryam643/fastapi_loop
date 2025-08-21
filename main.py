"""
FastAPI application for Store Monitoring System
Provides endpoints for triggering and retrieving reports
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import os
import logging
from report_service import ReportService
from database import init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Store Monitoring API",
    description="API for monitoring store uptime and generating reports",
    version="1.0.0"
)

# Response models
class TriggerReportResponse(BaseModel):
    report_id: str

class ReportStatusResponse(BaseModel):
    status: str
    created_at: str = None
    completed_at: str = None
    error: str = None

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Store Monitoring API",
        "version": "1.0.0",
        "endpoints": {
            "trigger_report": "/trigger_report",
            "get_report": "/get_report/{report_id}"
        }
    }

@app.post("/trigger_report", response_model=TriggerReportResponse)
async def trigger_report():
    """
    Trigger report generation from the data stored in DB
    
    Returns:
        report_id: Random string used for polling report status
    """
    try:
        logger.info("Report generation triggered via API")
        report_id = ReportService.trigger_report()
        
        return TriggerReportResponse(report_id=report_id)
        
    except Exception as e:
        logger.error(f"Error triggering report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger report generation: {str(e)}"
        )

@app.get("/get_report/{report_id}")
async def get_report(report_id: str):
    """
    Get report status or download CSV file
    
    Args:
        report_id: Report ID returned from trigger_report
        
    Returns:
        - If report is not complete: JSON with status "Running"
        - If report is complete: CSV file download
        - If report not found: 404 error
    """
    try:
        logger.info(f"Report status requested for ID: {report_id}")
        report_status = ReportService.get_report_status(report_id)
        
        # Handle error cases
        if "error" in report_status:
            if report_status["error"] == "Report not found":
                raise HTTPException(status_code=404, detail="Report not found")
            else:
                raise HTTPException(status_code=500, detail=report_status["error"])
        
        # If report is complete, return CSV file
        if report_status["status"] == "Complete":
            file_path = report_status["file_path"]
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Report file not found: {file_path}")
                raise HTTPException(status_code=500, detail="Report file not found")
            
            # Return CSV file
            return FileResponse(
                path=file_path,
                media_type='text/csv',
                filename=f"store_report_{report_id}.csv"
            )
        
        # If report is still running or failed, return status
        else:
            return JSONResponse(
                content={
                    "status": report_status["status"],
                    "created_at": report_status.get("created_at").isoformat() if report_status.get("created_at") else None
                }
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get report: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "store-monitoring-api"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
