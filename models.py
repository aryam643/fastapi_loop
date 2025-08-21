from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytz

Base = declarative_base()

class StoreStatus(Base):
    """Model for store status polling data"""
    __tablename__ = "store_status"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True, nullable=False)
    timestamp_utc = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # 'active' or 'inactive'
    
    def __repr__(self):
        return f"<StoreStatus(store_id={self.store_id}, timestamp={self.timestamp_utc}, status={self.status})>"

class BusinessHours(Base):
    """Model for store business hours"""
    __tablename__ = "business_hours"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time_local = Column(String, nullable=False)  # HH:MM:SS format
    end_time_local = Column(String, nullable=False)   # HH:MM:SS format
    
    def __repr__(self):
        return f"<BusinessHours(store_id={self.store_id}, day={self.day_of_week}, hours={self.start_time_local}-{self.end_time_local})>"

class StoreTimezone(Base):
    """Model for store timezone information"""
    __tablename__ = "store_timezones"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True, nullable=False, unique=True)
    timezone_str = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<StoreTimezone(store_id={self.store_id}, timezone={self.timezone_str})>"

class ReportStatus(Base):
    """Model for tracking report generation status"""
    __tablename__ = "report_status"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False)  # 'Running' or 'Complete'
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    file_path = Column(String, nullable=True)  # Path to generated CSV file
    
    def __repr__(self):
        return f"<ReportStatus(report_id={self.report_id}, status={self.status})>"

# Database configuration
DATABASE_URL = "sqlite:///./store_monitoring.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
