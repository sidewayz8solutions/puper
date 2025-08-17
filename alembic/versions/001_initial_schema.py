"""Initial schema for Puper API

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Note: PostGIS extension should be installed manually before running this migration
    # Run: CREATE EXTENSION IF NOT EXISTS postgis; in your database
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.Column('badges', sa.JSON(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_anonymous', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create restrooms table
    op.create_table('restrooms',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),  # Temporary: will be Geometry when PostGIS is available
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('address', sa.String(length=300), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('wheelchair_accessible', sa.String(length=20), nullable=True),
        sa.Column('gender_neutral', sa.Boolean(), nullable=True),
        sa.Column('baby_changing', sa.Boolean(), nullable=True),
        sa.Column('indoor', sa.Boolean(), nullable=True),
        sa.Column('requires_fee', sa.Boolean(), nullable=True),
        sa.Column('fee_amount', sa.Float(), nullable=True),
        sa.Column('unisex', sa.Boolean(), nullable=True),
        sa.Column('has_soap', sa.Boolean(), nullable=True),
        sa.Column('has_toilet_paper', sa.Boolean(), nullable=True),
        sa.Column('has_hand_dryer', sa.Boolean(), nullable=True),
        sa.Column('has_paper_towels', sa.Boolean(), nullable=True),
        sa.Column('has_hot_water', sa.Boolean(), nullable=True),
        sa.Column('has_mirror', sa.Boolean(), nullable=True),
        sa.Column('avg_cleanliness', sa.Float(), nullable=True),
        sa.Column('avg_lighting', sa.Float(), nullable=True),
        sa.Column('avg_safety', sa.Float(), nullable=True),
        sa.Column('avg_privacy', sa.Float(), nullable=True),
        sa.Column('avg_accessibility', sa.Float(), nullable=True),
        sa.Column('avg_overall', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('operating_hours', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('temporarily_closed', sa.Boolean(), nullable=True),
        sa.Column('permanently_closed', sa.Boolean(), nullable=True),
        sa.Column('submitter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(), nullable=True),
        sa.Column('extra_attributes', sa.JSON(), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['submitter_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_avg_overall_active', 'restrooms', ['avg_overall', 'is_active'], unique=False)
    op.create_index('idx_city_country', 'restrooms', ['city', 'country'], unique=False)
    # op.create_index('idx_location_spatial', 'restrooms', ['location'], unique=False, postgresql_using='gist')  # Requires PostGIS
    op.create_index(op.f('ix_restrooms_latitude'), 'restrooms', ['latitude'], unique=False)
    op.create_index(op.f('ix_restrooms_longitude'), 'restrooms', ['longitude'], unique=False)
    op.create_index(op.f('ix_restrooms_source'), 'restrooms', ['source'], unique=False)
    op.create_index(op.f('ix_restrooms_source_id'), 'restrooms', ['source_id'], unique=False)
    op.create_index(op.f('ix_restrooms_city'), 'restrooms', ['city'], unique=False)
    op.create_index(op.f('ix_restrooms_country'), 'restrooms', ['country'], unique=False)
    op.create_index(op.f('ix_restrooms_is_active'), 'restrooms', ['is_active'], unique=False)
    op.create_index(op.f('ix_restrooms_avg_overall'), 'restrooms', ['avg_overall'], unique=False)
    op.create_index(op.f('ix_restrooms_review_count'), 'restrooms', ['review_count'], unique=False)

    # Create reviews table
    op.create_table('reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('restroom_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cleanliness', sa.Integer(), nullable=False),
        sa.Column('lighting', sa.Integer(), nullable=False),
        sa.Column('safety', sa.Integer(), nullable=False),
        sa.Column('privacy', sa.Integer(), nullable=False),
        sa.Column('accessibility', sa.Integer(), nullable=False),
        sa.Column('overall', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=1000), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['restroom_id'], ['restrooms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_restroom_created', 'reviews', ['restroom_id', 'created_at'], unique=False)
    op.create_index('idx_user_reviews', 'reviews', ['user_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_reviews_created_at'), 'reviews', ['created_at'], unique=False)

    # Create favorites table
    op.create_table('favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('restroom_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['restroom_id'], ['restrooms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_restroom_unique', 'favorites', ['user_id', 'restroom_id'], unique=True)

    # Create reports table
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('restroom_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['restroom_id'], ['restrooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('favorites')
    op.drop_table('reviews')
    op.drop_table('restrooms')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS postgis')
