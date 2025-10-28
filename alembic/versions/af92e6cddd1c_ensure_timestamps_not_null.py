"""ensure_timestamps_not_null

Revision ID: af92e6cddd1c
Revises: 00ac68bf1bc1
Create Date: 2025-10-28 19:04:21.023381

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "af92e6cddd1c"
down_revision: Union[str, None] = "00ac68bf1bc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Atualizar registros existentes primeiro
    op.execute(
        """
        UPDATE degustacoes 
        SET created_at = NOW() 
        WHERE created_at IS NULL
    """
    )

    op.execute(
        """
        UPDATE degustacoes 
        SET updated_at = COALESCE(created_at, NOW())
        WHERE updated_at IS NULL
    """
    )

    op.execute(
        """
        UPDATE despesas 
        SET created_at = NOW() 
        WHERE created_at IS NULL
    """
    )

    op.execute(
        """
        UPDATE despesas 
        SET updated_at = COALESCE(created_at, NOW())
        WHERE updated_at IS NULL
    """
    )

    op.execute(
        """
        UPDATE eventos 
        SET created_at = NOW() 
        WHERE created_at IS NULL
    """
    )

    op.execute(
        """
        UPDATE eventos 
        SET updated_at = COALESCE(created_at, NOW())
        WHERE updated_at IS NULL
    """
    )

    # Agora alterar as colunas para NOT NULL
    op.alter_column("degustacoes", "created_at", nullable=False)
    op.alter_column("degustacoes", "updated_at", nullable=False)
    op.alter_column("despesas", "created_at", nullable=False)
    op.alter_column("despesas", "updated_at", nullable=False)
    op.alter_column("eventos", "created_at", nullable=False)
    op.alter_column("eventos", "updated_at", nullable=False)


def downgrade():
    op.alter_column("degustacoes", "created_at", nullable=True)
    op.alter_column("degustacoes", "updated_at", nullable=True)
    op.alter_column("despesas", "created_at", nullable=True)
    op.alter_column("despesas", "updated_at", nullable=True)
    op.alter_column("eventos", "created_at", nullable=True)
    op.alter_column("eventos", "updated_at", nullable=True)
