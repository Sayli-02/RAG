"""HNSW index for cosine search on chunk embeddings.

Revision ID: 0003_hnsw_index
Revises: 0002_document_owner
Create Date: 2026-11-22

"""
from typing import Sequence, Union

from alembic import op


revision: str = "0003_hnsw_index"
down_revision: Union[str, None] = "0002_document_owner"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # vector_cosine_ops matches the <=> distance used by retrieval.
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_document_chunks_embedding_hnsw")
