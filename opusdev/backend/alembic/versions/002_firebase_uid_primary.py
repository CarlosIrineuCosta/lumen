"""Use Firebase UID as primary key

Revision ID: 002_firebase_uid_primary
Revises: 001_initial_schema
Create Date: 2025-01-14

This migration changes the architecture to use Firebase UID as the primary key
instead of PostgreSQL UUID, eliminating all ID mapping issues.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_firebase_uid_primary'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """
    Switch from UUID to Firebase UID as primary key
    This is a BREAKING change - ensure no active sessions during migration
    """
    
    # Step 1: Drop all foreign key constraints that reference users.id
    op.drop_constraint('photos_user_id_fkey', 'photos', type_='foreignkey')
    op.drop_constraint('user_specialties_user_id_fkey', 'user_specialties', type_='foreignkey')
    op.drop_constraint('user_connections_requester_id_fkey', 'user_connections', type_='foreignkey')
    op.drop_constraint('user_connections_target_id_fkey', 'user_connections', type_='foreignkey')
    op.drop_constraint('photo_collaborators_user_id_fkey', 'photo_collaborators', type_='foreignkey')
    op.drop_constraint('photo_interactions_user_id_fkey', 'photo_interactions', type_='foreignkey')
    
    # Step 2: Update photos table to use firebase_uid
    op.add_column('photos', sa.Column('user_firebase_uid', sa.String(128), nullable=True))
    op.execute("""
        UPDATE photos 
        SET user_firebase_uid = users.firebase_uid 
        FROM users 
        WHERE photos.user_id = users.id
    """)
    op.alter_column('photos', 'user_firebase_uid', nullable=False)
    op.drop_column('photos', 'user_id')
    op.alter_column('photos', 'user_firebase_uid', new_column_name='user_id')
    
    # Step 3: Update user_specialties table
    op.add_column('user_specialties', sa.Column('user_firebase_uid', sa.String(128), nullable=True))
    op.execute("""
        UPDATE user_specialties 
        SET user_firebase_uid = users.firebase_uid 
        FROM users 
        WHERE user_specialties.user_id = users.id
    """)
    op.alter_column('user_specialties', 'user_firebase_uid', nullable=False)
    op.drop_column('user_specialties', 'user_id')
    op.alter_column('user_specialties', 'user_firebase_uid', new_column_name='user_id')
    
    # Step 4: Update user_connections table
    op.add_column('user_connections', sa.Column('requester_firebase_uid', sa.String(128), nullable=True))
    op.add_column('user_connections', sa.Column('target_firebase_uid', sa.String(128), nullable=True))
    op.execute("""
        UPDATE user_connections 
        SET requester_firebase_uid = u1.firebase_uid,
            target_firebase_uid = u2.firebase_uid
        FROM users u1, users u2
        WHERE user_connections.requester_id = u1.id 
        AND user_connections.target_id = u2.id
    """)
    op.alter_column('user_connections', 'requester_firebase_uid', nullable=False)
    op.alter_column('user_connections', 'target_firebase_uid', nullable=False)
    op.drop_column('user_connections', 'requester_id')
    op.drop_column('user_connections', 'target_id')
    op.alter_column('user_connections', 'requester_firebase_uid', new_column_name='requester_id')
    op.alter_column('user_connections', 'target_firebase_uid', new_column_name='target_id')
    
    # Step 5: Update photo_collaborators table
    op.add_column('photo_collaborators', sa.Column('user_firebase_uid', sa.String(128), nullable=True))
    op.execute("""
        UPDATE photo_collaborators 
        SET user_firebase_uid = users.firebase_uid 
        FROM users 
        WHERE photo_collaborators.user_id = users.id
    """)
    # Note: user_id can be NULL for text-only collaborators
    op.drop_column('photo_collaborators', 'user_id')
    op.alter_column('photo_collaborators', 'user_firebase_uid', new_column_name='user_id')
    
    # Step 6: Update photo_interactions table
    op.add_column('photo_interactions', sa.Column('user_firebase_uid', sa.String(128), nullable=True))
    op.execute("""
        UPDATE photo_interactions 
        SET user_firebase_uid = users.firebase_uid 
        FROM users 
        WHERE photo_interactions.user_id = users.id
    """)
    op.alter_column('photo_interactions', 'user_firebase_uid', nullable=False)
    op.drop_column('photo_interactions', 'user_id')
    op.alter_column('photo_interactions', 'user_firebase_uid', new_column_name='user_id')
    
    # Step 7: Drop the old users.id column and make firebase_uid the primary key
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_column('users', 'id')
    op.alter_column('users', 'firebase_uid', new_column_name='id')
    op.create_primary_key('users_pkey', 'users', ['id'])
    
    # Step 8: Re-create all foreign key constraints
    op.create_foreign_key('photos_user_id_fkey', 'photos', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('user_specialties_user_id_fkey', 'user_specialties', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('user_connections_requester_id_fkey', 'user_connections', 'users', ['requester_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('user_connections_target_id_fkey', 'user_connections', 'users', ['target_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('photo_collaborators_user_id_fkey', 'photo_collaborators', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('photo_interactions_user_id_fkey', 'photo_interactions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    
    # Step 9: Create indexes for performance
    op.create_index('idx_photos_user_id', 'photos', ['user_id'])
    op.create_index('idx_user_specialties_user_id', 'user_specialties', ['user_id'])
    op.create_index('idx_user_connections_requester', 'user_connections', ['requester_id'])
    op.create_index('idx_user_connections_target', 'user_connections', ['target_id'])
    op.create_index('idx_photo_collaborators_user_id', 'photo_collaborators', ['user_id'])
    op.create_index('idx_photo_interactions_user_id', 'photo_interactions', ['user_id'])


def downgrade():
    """
    Revert to UUID primary keys (NOT RECOMMENDED)
    This is complex and may result in data loss
    """
    raise NotImplementedError("Downgrade not supported - this is a one-way migration")
