"""add site names

Revision ID: b7f67e834993
Revises: d3721b4507b4
Create Date: 2023-11-02 01:10:43.503216

"""
from alembic import op
import sqlalchemy as sa
from app.models.base import get_engine
from sqlalchemy.orm import Session
from app.models.pharmacies import SiteName


# revision identifiers, used by Alembic.
revision = 'b7f67e834993'
down_revision = 'd3721b4507b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    site_names = ['farmani', 'aptechestvo']
    with Session(get_engine()) as session:
        for site_name in site_names:
            obj = SiteName(title=site_name)
            session.add(obj)
            session.commit()



def downgrade() -> None:
    pass
