"""unificacao_tabelas_vendas_e_eventos

Revision ID: a97f4d5a8c38
Revises: 0867e4903a57
Create Date: 2025-10-27 13:49:17.315649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a97f4d5a8c38'
down_revision: Union[str, None] = '0867e4903a57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
        # Passo 1: Adicionar as novas colunas à tabela 'eventos'
        op.add_column('eventos', sa.Column('vlr_unitario_por_convidado', sa.Numeric(10, 2), nullable=True))
        op.add_column('eventos', sa.Column('vlr_total_contrato', sa.Numeric(10, 2), nullable=True))
        op.add_column('eventos', sa.Column('data_venda', sa.DateTime, nullable=True))
        op.add_column('eventos', sa.Column('observacoes_venda', sa.Text, nullable=True))

        # Passo 2: Migrar os dados da tabela 'vendas' para 'eventos'
        # Usamos SQL puro aqui para a atualização baseada em um JOIN
        op.execute("""
            UPDATE eventos
            SET
                vlr_unitario_por_convidado = vendas.vlr_unitario_por_convidado,
                vlr_total_contrato = vendas.vlr_total_contrato,
                data_venda = vendas.data_venda,
                observacoes_venda = vendas.observacoes
            FROM vendas
            WHERE eventos.id = vendas.id_evento
        """)

        # Passo 3: Remover a tabela 'vendas'
        op.drop_table('vendas')


def downgrade():
        # Para reverter, precisamos recriar a tabela 'vendas' e mover os dados de volta.
        # Passo 1: Recriar a tabela 'vendas'
        op.create_table('vendas',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
            sa.Column('id_evento', sa.Integer(), sa.ForeignKey('eventos.id'), nullable=False, unique=True),
            sa.Column('vlr_unitario_por_convidado', sa.Numeric(10, 2), nullable=True),
            # ... recriar todas as colunas originais de 'vendas'
        )

        # Passo 2: Mover os dados de volta (mais complexo, mas importante para um downgrade completo)
        op.execute("""
            INSERT INTO vendas (id_evento, vlr_unitario_por_convidado, vlr_total_contrato, data_venda, observacoes, id_usuario_criador, created_at, updated_at)
            SELECT id, vlr_unitario_por_convidado, vlr_total_contrato, data_venda, observacoes_venda, id_usuario_criador, created_at, updated_at
            FROM eventos
            WHERE vlr_total_contrato IS NOT NULL
        """)

        # Passo 3: Remover as colunas da tabela 'eventos'
        op.drop_column('eventos', 'observacoes_venda')
        op.drop_column('eventos', 'data_venda')
        op.drop_column('eventos', 'vlr_total_contrato')
        op.drop_column('eventos', 'vlr_unitario_por_convidado')
