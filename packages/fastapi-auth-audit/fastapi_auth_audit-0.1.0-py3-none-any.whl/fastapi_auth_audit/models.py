import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base
from .config import settings

class AuditLog(Base):
    __tablename__ = settings.AUDIT_TABLE_NAME

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    resource = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    detail = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
