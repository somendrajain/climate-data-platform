from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.user import UserRole
from app.models.dataset import DatasetDomain, ChartType, DatasetStatus
from app.models.review import ReviewAction


# User schemas
class UserBrief(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


# Record schemas
class DatasetRecordCreate(BaseModel):
    label: str
    value: float
    metadata_payload: Optional[dict[str, Any]] = None
    sort_order: int = 0


class DatasetRecordOut(BaseModel):
    id: int
    label: str
    value: float
    metadata_payload: Optional[dict[str, Any]] = None
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


# Review schemas
class DatasetReviewCreate(BaseModel):
    action: ReviewAction
    comments: Optional[str] = None


class DatasetReviewOut(BaseModel):
    id: int
    action: ReviewAction
    comments: Optional[str] = None
    created_at: datetime
    reviewer: Optional[UserBrief] = None

    model_config = ConfigDict(from_attributes=True)


# Dataset creation & update schemas
class DatasetCreate(BaseModel):
    title: str
    description: Optional[str] = None
    domain: DatasetDomain
    chart_type: ChartType
    publication_order: int = 0
    records: List[DatasetRecordCreate] = []


# Dataset schemas
class DatasetBrief(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    domain: DatasetDomain
    chart_type: ChartType
    status: DatasetStatus
    publication_order: int
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserBrief] = None

    model_config = ConfigDict(from_attributes=True)


class DatasetDetail(DatasetBrief):
    records: List[DatasetRecordOut] = []
    reviews: List[DatasetReviewOut] = []

    model_config = ConfigDict(from_attributes=True)
