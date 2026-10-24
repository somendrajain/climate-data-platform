from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.dataset import Dataset, DatasetDomain, DatasetStatus
from app.schemas.dataset import DatasetBrief, DatasetDetail

router = APIRouter()


@router.get("", response_model=List[DatasetBrief])
def get_datasets(
    domain: Optional[DatasetDomain] = Query(None, description="Filter by domain (CLIMATE, ENERGY, POWER)"),
    status: Optional[DatasetStatus] = Query(None, description="Filter by status (e.g. PUBLISHED)"),
    db: Session = Depends(get_db),
):
    """
    Retrieve datasets ordered by publication_order and updated_at.
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
    Retrieve full dataset detail including validated structured records and review history.
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
