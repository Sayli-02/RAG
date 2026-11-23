"""Initial schema with pgvector extension and all core tables.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 3. Documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('authority', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index('idx_documents_authority_category_status', 'documents', ['authority', 'category', 'status'], unique=False)

    # 4. Document Versions table
    op.create_table(
        'document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.String(length=50), nullable=False, server_default='1.0'),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('parent_version_id', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_version_id'], ['document_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_versions_id'), 'document_versions', ['id'], unique=False)
    op.create_index(op.f('ix_document_versions_document_id'), 'document_versions', ['document_id'], unique=False)

    # 5. Document Chunks table (with pgvector)
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=True),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_id'], ['document_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_id'), 'document_chunks', ['id'], unique=False)
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_chunks_version_id'), 'document_chunks', ['version_id'], unique=False)
    op.create_index('idx_document_chunks_doc_version', 'document_chunks', ['document_id', 'version_id'], unique=False)

    # 6. Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='New Conversation'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # 7. Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)

    # 8. Citations table
    op.create_table(
        'citations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('chunk_id', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['chunk_id'], ['document_chunks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_citations_id'), 'citations', ['id'], unique=False)
    op.create_index(op.f('ix_citations_message_id'), 'citations', ['message_id'], unique=False)
    op.create_index(op.f('ix_citations_chunk_id'), 'citations', ['chunk_id'], unique=False)

    # 9. Comparison Reports table
    op.create_table(
        'comparison_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('version_a_id', sa.Integer(), nullable=False),
        sa.Column('version_b_id', sa.Integer(), nullable=False),
        sa.Column('report_json', sa.JSON(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_a_id'], ['document_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_b_id'], ['document_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comparison_reports_id'), 'comparison_reports', ['id'], unique=False)
    op.create_index(op.f('ix_comparison_reports_user_id'), 'comparison_reports', ['user_id'], unique=False)

    # 10. Compliance Checklists table
    op.create_table(
        'compliance_checklists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_checklists_id'), 'compliance_checklists', ['id'], unique=False)
    op.create_index(op.f('ix_compliance_checklists_user_id'), 'compliance_checklists', ['user_id'], unique=False)
    op.create_index(op.f('ix_compliance_checklists_document_id'), 'compliance_checklists', ['document_id'], unique=False)

    # 11. Compliance Requirements table
    op.create_table(
        'compliance_requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('checklist_id', sa.Integer(), nullable=False),
        sa.Column('requirement_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('authority', sa.String(length=50), nullable=True),
        sa.Column('source_chunk_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending_review'),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['checklist_id'], ['compliance_checklists.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_chunk_id'], ['document_chunks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_requirements_id'), 'compliance_requirements', ['id'], unique=False)
    op.create_index(op.f('ix_compliance_requirements_checklist_id'), 'compliance_requirements', ['checklist_id'], unique=False)

    # 12. Saved Queries table
    op.create_table(
        'saved_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_queries_id'), 'saved_queries', ['id'], unique=False)
    op.create_index(op.f('ix_saved_queries_user_id'), 'saved_queries', ['user_id'], unique=False)

    # 13. Evaluation Runs table
    op.create_table(
        'evaluation_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_name', sa.String(length=255), nullable=False),
        sa.Column('dataset_name', sa.String(length=255), nullable=False),
        sa.Column('metrics_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evaluation_runs_id'), 'evaluation_runs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('evaluation_runs')
    op.drop_table('saved_queries')
    op.drop_table('compliance_requirements')
    op.drop_table('compliance_checklists')
    op.drop_table('comparison_reports')
    op.drop_table('citations')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('document_chunks')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('users')
    op.execute("DROP EXTENSION IF EXISTS vector;")

