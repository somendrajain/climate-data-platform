from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base


class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, default="api")
    status = Column(String, default="ok")
    checked_at = Column(DateTime, default=datetime.utcnow)
