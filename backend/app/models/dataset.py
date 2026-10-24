import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class DatasetDomain(str, enum.Enum):
    CLIMATE = "CLIMATE"
    ENERGY = "ENERGY"
    POWER = "POWER"


class ChartType(str, enum.Enum):
    LINE = "LINE"
    BAR = "BAR"
    AREA = "AREA"
    PIE = "PIE"
    SCATTER = "SCATTER"


class DatasetStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    domain = Column(SQLEnum(DatasetDomain), nullable=False, index=True)
    chart_type = Column(SQLEnum(ChartType), nullable=False)
    status = Column(
        SQLEnum(DatasetStatus),
        nullable=False,
        default=DatasetStatus.DRAFT,
        index=True,
    )
    publication_order = Column(Integer, default=0, nullable=False, index=True)

    creator_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    creator = relationship(
        "User", back_populates="created_datasets", foreign_keys=[creator_id]
    )
    records = relationship(
        "DatasetRecord",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="DatasetRecord.sort_order",
    )
    reviews = relationship(
        "DatasetReview",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="DatasetReview.created_at",
    )


class DatasetRecord(Base):
    """
    Validated structured data point for each dataset visualization type.
    """
    __tablename__ = "dataset_records"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(
        Integer,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label = Column(String(255), nullable=False)  # e.g., "1990", "Solar", "Jan 2024"
    value = Column(Float, nullable=False)        # numeric metric value
    metadata_payload = Column(JSON, nullable=True)  # optional tags, coordinates, units
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="records")
