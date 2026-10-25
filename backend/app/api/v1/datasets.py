from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.user import User
from app.models.dataset import Dataset, DatasetRecord, DatasetDomain, DatasetStatus
from app.models.review import DatasetReview, ReviewAction
from app.schemas.dataset import (
    DatasetBrief,
    DatasetDetail,
    DatasetCreate,
    DatasetReviewCreate,
    DatasetReviewOut,
)
from app.api.deps import require_admin, require_super_admin

router = APIRouter()


# -------------------------------------------------------------
# PUBLIC ENDPOINTS (No authentication required)
# -------------------------------------------------------------

@router.get("", response_model=List[DatasetBrief])
def get_datasets(
    domain: Optional[DatasetDomain] = Query(None, description="Filter by domain (CLIMATE, ENERGY, POWER)"),
    status: Optional[DatasetStatus] = Query(None, description="Filter by status (e.g. PUBLISHED)"),
    db: Session = Depends(get_db),
):
    """
    PUBLIC: Retrieve datasets ordered by publication_order.
    Accessible by anyone without logging in.
    """
    query = db.query(Dataset).options(joinedload(Dataset.creator))
    if domain:
        query = query.filter(Dataset.domain == domain)
    if status:
        query = query.filter(Dataset.status == status)

    return query.order_by(Dataset.publication_order.asc(), Dataset.updated_at.desc()).all()


@router.get("/{dataset_id}", response_model=DatasetDetail)
def get_dataset_by_id(dataset_id: int, db: Session = Depends(get_db)):
    """
    PUBLIC: Retrieve full dataset detail with records and review history.
    Accessible by anyone without logging in.
    """
    dataset = (
        db.query(Dataset)
        .options(
            joinedload(Dataset.creator),
            joinedload(Dataset.records),
            joinedload(Dataset.reviews),
        )
        .filter(Dataset.id == dataset_id)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return dataset


# -------------------------------------------------------------
# PROTECTED: ADMIN & SUPER_ADMIN (Dataset creation)
# -------------------------------------------------------------

@router.post("", response_model=DatasetDetail, status_code=status.HTTP_201_CREATED)
def create_dataset(
    dataset_in: DatasetCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    PROTECTED (ADMIN or SUPER_ADMIN):
    Create a new dataset draft and its structured data records.
    """
    new_dataset = Dataset(
        title=dataset_in.title,
        description=dataset_in.description,
        domain=dataset_in.domain,
        chart_type=dataset_in.chart_type,
        status=DatasetStatus.DRAFT,
        publication_order=dataset_in.publication_order,
        creator_id=current_user.id,
    )
    db.add(new_dataset)
    db.flush()

    # Add records
    for rec in dataset_in.records:
        record_obj = DatasetRecord(
            dataset_id=new_dataset.id,
            label=rec.label,
            value=rec.value,
            metadata_payload=rec.metadata_payload,
            sort_order=rec.sort_order,
        )
        db.add(record_obj)

    # Initial review entry
    review_obj = DatasetReview(
        dataset_id=new_dataset.id,
        reviewer_id=current_user.id,
        action=ReviewAction.SUBMITTED,
        comments="Dataset draft created and submitted for review.",
    )
    db.add(review_obj)

    db.commit()
    db.refresh(new_dataset)
    return new_dataset


# -------------------------------------------------------------
# PROTECTED: SUPER_ADMIN ONLY (Dataset Approval & Publishing)
# -------------------------------------------------------------

@router.post("/{dataset_id}/reviews", response_model=DatasetReviewOut, status_code=status.HTTP_201_CREATED)
def review_and_approve_dataset(
    dataset_id: int,
    review_in: DatasetReviewCreate,
    current_super_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    PROTECTED (SUPER_ADMIN ONLY):
    Review, approve, or publish a dataset.
    Standard Admins receive 403 Forbidden on this endpoint.
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Update dataset status based on review action
    if review_in.action == ReviewAction.APPROVED:
        dataset.status = DatasetStatus.IN_REVIEW
    elif review_in.action == ReviewAction.PUBLISHED:
        dataset.status = DatasetStatus.PUBLISHED
    elif review_in.action == ReviewAction.REJECTED:
        dataset.status = DatasetStatus.DRAFT

    # Record review entry
    review_entry = DatasetReview(
        dataset_id=dataset.id,
        reviewer_id=current_super_admin.id,
        action=review_in.action,
        comments=review_in.comments,
    )
    db.add(review_entry)
    db.commit()
    db.refresh(review_entry)

    return review_entry
