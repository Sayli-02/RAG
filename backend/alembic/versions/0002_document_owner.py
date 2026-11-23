"""Add document owner and ingestion error message.

Revision ID: 0002_document_owner
Revises: 0001_initial_schema
Create Date: 2026-11-22

Assumes the documents table has no rows yet. Adding uploaded_by as NOT NULL
fails if rows already exist.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_document_owner"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("uploaded_by", sa.Integer(), nullable=False))
    op.add_column("documents", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_foreign_key(
        "fk_documents_uploaded_by_users",
        "documents",
        "users",
        ["uploaded_by"],
        ["id"],
    )
    op.create_index("ix_documents_uploaded_by", "documents", ["uploaded_by"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_documents_uploaded_by", table_name="documents")
    op.drop_constraint("fk_documents_uploaded_by_users", "documents", type_="foreignkey")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "uploaded_by")
