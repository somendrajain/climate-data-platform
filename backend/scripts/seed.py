"""
Database seed script for Milestone 2.
Seeds:
- Users with Admin and Super Admin roles.
- Sample datasets for Climate, Energy, and Power domains with distinct visualization types.
- Structured dataset records for Line, Bar, and Pie charts.
- Review and publication approval histories.
Uses a single atomic database transaction.
"""

import sys
import os
from datetime import datetime, timedelta

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.dataset import (
    Dataset,
    DatasetRecord,
    DatasetDomain,
    ChartType,
    DatasetStatus,
)
from app.models.review import DatasetReview, ReviewAction


def seed_database():
    db = SessionLocal()
    try:
        print("🌱 Starting database seed...")

        # 1. Clean existing sample data in reverse dependency order
        db.query(DatasetRecord).delete()
        db.query(DatasetReview).delete()
        db.query(Dataset).delete()
        db.query(User).delete()
        db.commit()

        # 2. Seed Users with secure hashed passwords
        super_admin = User(
            email="superadmin@climatedata.org",
            full_name="Sarah Connor (Super Admin)",
            role=UserRole.SUPER_ADMIN,
            hashed_password=get_password_hash("SuperAdminPass123!"),
            is_active=True,
        )
        admin = User(
            email="admin@climatedata.org",
            full_name="Alex Rivera (Data Admin)",
            role=UserRole.ADMIN,
            hashed_password=get_password_hash("AdminPass123!"),
            is_active=True,
        )
        db.add_all([super_admin, admin])
        db.flush()  # Populates user IDs without ending the transaction
        print(f"✅ Created users with hashed passwords: {super_admin.email}, {admin.email}")

        now = datetime.utcnow()

        # 3. Seed Dataset 1: Climate (Line Chart)
        climate_dataset = Dataset(
            title="Global Mean Surface Temperature Anomalies (1980–2024)",
            description="Annual temperature deviations relative to the 1951-1980 average base period (°C). Data reflects NASA GISTEMP observations.",
            domain=DatasetDomain.CLIMATE,
            chart_type=ChartType.LINE,
            status=DatasetStatus.PUBLISHED,
            publication_order=1,
            creator_id=admin.id,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=1),
        )
        db.add(climate_dataset)
        db.flush()

        climate_points = [
            ("1980", 0.26, {"unit": "°C", "confidence": "high"}),
            ("1985", 0.12, {"unit": "°C", "confidence": "high"}),
            ("1990", 0.45, {"unit": "°C", "confidence": "high"}),
            ("1995", 0.45, {"unit": "°C", "confidence": "high"}),
            ("2000", 0.39, {"unit": "°C", "confidence": "high"}),
            ("2005", 0.68, {"unit": "°C", "confidence": "high"}),
            ("2010", 0.72, {"unit": "°C", "confidence": "high"}),
            ("2015", 0.90, {"unit": "°C", "confidence": "high"}),
            ("2020", 1.02, {"unit": "°C", "confidence": "high"}),
            ("2024", 1.28, {"unit": "°C", "confidence": "high"}),
        ]
        for idx, (label, val, meta) in enumerate(climate_points):
            db.add(
                DatasetRecord(
                    dataset_id=climate_dataset.id,
                    label=label,
                    value=val,
                    metadata_payload=meta,
                    sort_order=idx + 1,
                )
            )

        # Review history for Climate Dataset
        db.add_all([
            DatasetReview(
                dataset_id=climate_dataset.id,
                reviewer_id=admin.id,
                action=ReviewAction.SUBMITTED,
                comments="Initial ingest of NASA GISTEMP annual series for peer review.",
                created_at=now - timedelta(days=9),
            ),
            DatasetReview(
                dataset_id=climate_dataset.id,
                reviewer_id=super_admin.id,
                action=ReviewAction.APPROVED,
                comments="Verified baseline calculations against 1951-1980 climatology.",
                created_at=now - timedelta(days=5),
            ),
            DatasetReview(
                dataset_id=climate_dataset.id,
                reviewer_id=super_admin.id,
                action=ReviewAction.PUBLISHED,
                comments="Published as primary headline indicator.",
                created_at=now - timedelta(days=1),
            ),
        ])
        print("✅ Seeded CLIMATE dataset with 10 records and 3 review entries")

        # 4. Seed Dataset 2: Energy (Bar Chart)
        energy_dataset = Dataset(
            title="Global Renewable Electricity Generation by Source (TWh)",
            description="Annual clean generation in Terawatt-hours (TWh) from modern renewable energy sources.",
            domain=DatasetDomain.ENERGY,
            chart_type=ChartType.BAR,
            status=DatasetStatus.PUBLISHED,
            publication_order=2,
            creator_id=admin.id,
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=2),
        )
        db.add(energy_dataset)
        db.flush()

        energy_points = [
            ("Solar Photovoltaic", 1630.0, {"unit": "TWh", "growth_yoy": "+24%"}),
            ("Wind Power (Onshore/Offshore)", 2304.0, {"unit": "TWh", "growth_yoy": "+11%"}),
            ("Hydropower", 4210.0, {"unit": "TWh", "growth_yoy": "-1%"}),
            ("Bioenergy", 685.0, {"unit": "TWh", "growth_yoy": "+3%"}),
            ("Geothermal", 95.0, {"unit": "TWh", "growth_yoy": "+2%"}),
        ]
        for idx, (label, val, meta) in enumerate(energy_points):
            db.add(
                DatasetRecord(
                    dataset_id=energy_dataset.id,
                    label=label,
                    value=val,
                    metadata_payload=meta,
                    sort_order=idx + 1,
                )
            )

        # Review history for Energy Dataset
        db.add_all([
            DatasetReview(
                dataset_id=energy_dataset.id,
                reviewer_id=admin.id,
                action=ReviewAction.SUBMITTED,
                comments="Ingested IEA World Energy Outlook dataset.",
                created_at=now - timedelta(days=6),
            ),
            DatasetReview(
                dataset_id=energy_dataset.id,
                reviewer_id=super_admin.id,
                action=ReviewAction.PUBLISHED,
                comments="Approved and scheduled for energy transition dashboard.",
                created_at=now - timedelta(days=2),
            ),
        ])
        print("✅ Seeded ENERGY dataset with 5 records and 2 review entries")

        # 5. Seed Dataset 3: Power (Pie Chart)
        power_dataset = Dataset(
            title="Global Power Generation Mix Percentage",
            description="Percentage share of worldwide electricity generation by power technology.",
            domain=DatasetDomain.POWER,
            chart_type=ChartType.PIE,
            status=DatasetStatus.PUBLISHED,
            publication_order=3,
            creator_id=super_admin.id,
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(hours=6),
        )
        db.add(power_dataset)
        db.flush()

        power_points = [
            ("Coal", 35.4, {"unit": "%", "category": "Fossil"}),
            ("Natural Gas", 22.1, {"unit": "%", "category": "Fossil"}),
            ("Hydropower", 14.3, {"unit": "%", "category": "Renewable"}),
            ("Nuclear", 9.1, {"unit": "%", "category": "Clean/Firm"}),
            ("Wind", 7.8, {"unit": "%", "category": "Renewable"}),
            ("Solar", 5.5, {"unit": "%", "category": "Renewable"}),
            ("Other (Oil/Bio)", 5.8, {"unit": "%", "category": "Mixed"}),
        ]
        for idx, (label, val, meta) in enumerate(power_points):
            db.add(
                DatasetRecord(
                    dataset_id=power_dataset.id,
                    label=label,
                    value=val,
                    metadata_payload=meta,
                    sort_order=idx + 1,
                )
            )

        db.add(
            DatasetReview(
                dataset_id=power_dataset.id,
                reviewer_id=super_admin.id,
                action=ReviewAction.PUBLISHED,
                comments="Published direct benchmark dataset for global power sector mix.",
                created_at=now - timedelta(hours=6),
            )
        )
        print("✅ Seeded POWER dataset with 7 records and 1 review entry")

        # Commit everything as one atomic transaction
        db.commit()
        print("🎉 Database successfully seeded with Climate, Energy, and Power datasets!")

    except Exception as exc:
        db.rollback()
        print(f"❌ Error during seeding: {exc}")
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
