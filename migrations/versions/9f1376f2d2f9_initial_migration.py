"""initial migration

Revision ID: 9f1376f2d2f9
Revises: 
Create Date: 2018-05-07 23:26:03.701867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f1376f2d2f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('vineyards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vineyards_user_id'), 'vineyards', ['user_id'], unique=False)
    op.create_table('sensors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('gateway', sa.String(length=256), nullable=True),
    sa.Column('power_perc', sa.Float(), nullable=True),
    sa.Column('vineyard_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vineyard_id'], ['vineyards.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensors_user_id'), 'sensors', ['user_id'], unique=False)
    op.create_table('magnitudes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('layer', sa.Enum('Surface', 'Depth 1', 'Depth 2', name='sensor_layers'), nullable=False),
    sa.Column('type', sa.Enum('Temperature', 'Humidity', 'Conductivity', 'pH', 'Light', 'Dew', name='sensor_types'), nullable=False),
    sa.Column('sensor_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensors.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_layer_type', 'magnitudes', ['user_id', 'layer', 'type'], unique=False)
    op.create_index(op.f('ix_magnitudes_layer'), 'magnitudes', ['layer'], unique=False)
    op.create_index(op.f('ix_magnitudes_type'), 'magnitudes', ['type'], unique=False)
    op.create_index(op.f('ix_magnitudes_user_id'), 'magnitudes', ['user_id'], unique=False)
    op.create_table('metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('magnitude_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['magnitude_id'], ['magnitudes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metrics_magnitude_id'), 'metrics', ['magnitude_id'], unique=False)
    op.create_index(op.f('ix_metrics_timestamp'), 'metrics', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_metrics_timestamp'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_magnitude_id'), table_name='metrics')
    op.drop_table('metrics')
    op.drop_index(op.f('ix_magnitudes_user_id'), table_name='magnitudes')
    op.drop_index(op.f('ix_magnitudes_type'), table_name='magnitudes')
    op.drop_index(op.f('ix_magnitudes_layer'), table_name='magnitudes')
    op.drop_index('idx_user_layer_type', table_name='magnitudes')
    op.drop_table('magnitudes')
    op.drop_index(op.f('ix_sensors_user_id'), table_name='sensors')
    op.drop_table('sensors')
    op.drop_index(op.f('ix_vineyards_user_id'), table_name='vineyards')
    op.drop_table('vineyards')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
