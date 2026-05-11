"""refactor leads to N-N via campaign_leads

Revision ID: a3f9c1d2e8b5
Revises: db75def3e90f
Create Date: 2026-05-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a3f9c1d2e8b5'
down_revision: Union[str, Sequence[str], None] = 'db75def3e90f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# leadstatus enum já existe no banco desde a migration inicial
_leadstatus = postgresql.ENUM(
    'novo', 'contatado', 'qualificado', 'convertido', 'descartado',
    name='leadstatus',
    create_type=False,
)


def upgrade() -> None:
    # 1. Criar tabela campaign_leads
    op.create_table(
        'campaign_leads',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('campaign_id', sa.Uuid(), nullable=False),
        sa.Column('lead_id', sa.Uuid(), nullable=False),
        sa.Column('status', _leadstatus, nullable=False),
        sa.Column(
            'entrada_em',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('campaign_id', 'lead_id', name='uq_campaign_lead'),
    )

    # 2. Migrar dados existentes de leads → campaign_leads
    op.execute("""
        INSERT INTO campaign_leads (id, campaign_id, lead_id, status, entrada_em)
        SELECT gen_random_uuid(), campaign_id, id, status, created_at
        FROM leads
        WHERE campaign_id IS NOT NULL
    """)

    # ── messages ────────────────────────────────────────────────────────────

    # 3. Adicionar campaign_lead_id (nullable por enquanto) em messages
    op.add_column('messages', sa.Column('campaign_lead_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'messages_campaign_lead_id_fkey',
        'messages', 'campaign_leads',
        ['campaign_lead_id'], ['id'],
        ondelete='CASCADE',
    )

    # 4. Preencher campaign_lead_id nos messages existentes
    op.execute("""
        UPDATE messages
        SET campaign_lead_id = cl.id
        FROM campaign_leads cl
        WHERE cl.campaign_id = messages.campaign_id
          AND cl.lead_id = messages.lead_id
    """)

    # 5. Remover colunas antigas de messages
    op.drop_constraint('messages_campaign_id_fkey', 'messages', type_='foreignkey')
    op.drop_constraint('messages_lead_id_fkey', 'messages', type_='foreignkey')
    op.drop_column('messages', 'campaign_id')
    op.drop_column('messages', 'lead_id')

    # 6. Tornar campaign_lead_id obrigatório em messages
    op.alter_column('messages', 'campaign_lead_id', nullable=False)

    # ── events ──────────────────────────────────────────────────────────────

    # 7. Adicionar campaign_lead_id (nullable por enquanto) em events
    op.add_column('events', sa.Column('campaign_lead_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'events_campaign_lead_id_fkey',
        'events', 'campaign_leads',
        ['campaign_lead_id'], ['id'],
        ondelete='CASCADE',
    )

    # 8. Preencher campaign_lead_id nos events existentes
    op.execute("""
        UPDATE events
        SET campaign_lead_id = cl.id
        FROM campaign_leads cl
        WHERE cl.campaign_id = events.campaign_id
          AND cl.lead_id = events.lead_id
    """)

    # 9. Remover colunas antigas de events
    op.drop_constraint('events_campaign_id_fkey', 'events', type_='foreignkey')
    op.drop_constraint('events_lead_id_fkey', 'events', type_='foreignkey')
    op.drop_column('events', 'campaign_id')
    op.drop_column('events', 'lead_id')

    # 10. Tornar campaign_lead_id obrigatório em events
    op.alter_column('events', 'campaign_lead_id', nullable=False)

    # ── leads ───────────────────────────────────────────────────────────────

    # 11. Remover campaign_id e status de leads
    op.drop_constraint('leads_campaign_id_fkey', 'leads', type_='foreignkey')
    op.drop_column('leads', 'campaign_id')
    op.drop_column('leads', 'status')


def downgrade() -> None:
    # ── leads ───────────────────────────────────────────────────────────────

    # Restaurar status e campaign_id em leads
    op.add_column('leads', sa.Column('status', _leadstatus, nullable=True))
    op.add_column('leads', sa.Column('campaign_id', sa.Uuid(), nullable=True))

    # Restaurar dados (um registro por lead; se N:N, pega o primeiro)
    op.execute("""
        UPDATE leads l
        SET campaign_id = cl.campaign_id,
            status      = cl.status
        FROM campaign_leads cl
        WHERE cl.lead_id = l.id
    """)

    op.alter_column('leads', 'campaign_id', nullable=False)
    op.alter_column('leads', 'status', nullable=False)
    op.create_foreign_key(
        'leads_campaign_id_fkey', 'leads', 'campaigns',
        ['campaign_id'], ['id'], ondelete='CASCADE',
    )

    # ── events ──────────────────────────────────────────────────────────────

    op.add_column('events', sa.Column('campaign_id', sa.Uuid(), nullable=True))
    op.add_column('events', sa.Column('lead_id', sa.Uuid(), nullable=True))

    op.execute("""
        UPDATE events e
        SET campaign_id = cl.campaign_id,
            lead_id     = cl.lead_id
        FROM campaign_leads cl
        WHERE cl.id = e.campaign_lead_id
    """)

    op.alter_column('events', 'campaign_id', nullable=False)
    op.create_foreign_key(
        'events_campaign_id_fkey', 'events', 'campaigns',
        ['campaign_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'events_lead_id_fkey', 'events', 'leads',
        ['lead_id'], ['id'], ondelete='SET NULL',
    )
    op.drop_constraint('events_campaign_lead_id_fkey', 'events', type_='foreignkey')
    op.drop_column('events', 'campaign_lead_id')

    # ── messages ────────────────────────────────────────────────────────────

    op.add_column('messages', sa.Column('campaign_id', sa.Uuid(), nullable=True))
    op.add_column('messages', sa.Column('lead_id', sa.Uuid(), nullable=True))

    op.execute("""
        UPDATE messages m
        SET campaign_id = cl.campaign_id,
            lead_id     = cl.lead_id
        FROM campaign_leads cl
        WHERE cl.id = m.campaign_lead_id
    """)

    op.alter_column('messages', 'campaign_id', nullable=False)
    op.create_foreign_key(
        'messages_campaign_id_fkey', 'messages', 'campaigns',
        ['campaign_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'messages_lead_id_fkey', 'messages', 'leads',
        ['lead_id'], ['id'], ondelete='SET NULL',
    )
    op.drop_constraint('messages_campaign_lead_id_fkey', 'messages', type_='foreignkey')
    op.drop_column('messages', 'campaign_lead_id')

    # ── campaign_leads ───────────────────────────────────────────────────────

    op.drop_table('campaign_leads')
