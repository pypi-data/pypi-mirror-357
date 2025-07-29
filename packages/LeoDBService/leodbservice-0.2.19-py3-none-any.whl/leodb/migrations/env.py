import asyncio
import sys
from logging.config import fileConfig

# On Windows, the default asyncio event loop policy is not compatible with psycopg.
# We need to set a different policy.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import pool

from alembic import context

# Import your base model and all models that should be included in migrations
from leodb.models.base import Base
# Import settings from the application's config module
from leodb.core.config import settings
import leodb.models.general.account
import leodb.models.account.conversation
import leodb.models.account.data_source
import leodb.models.account.data_source_acct
import leodb.models.account.data_source_record
import leodb.models.account.data_source_scheduled_task
import leodb.models.account.data_source_user
import leodb.models.general.invoice
import leodb.models.general.package
import leodb.models.general.payment_method
import leodb.models.account.project
import leodb.models.account.project_output
import leodb.models.account.project_step
import leodb.models.account.project_step_data_source_association
import leodb.models.account.project_step_tool_association
import leodb.models.account.record
import leodb.models.account.scheduled_task
import leodb.models.account.scheduled_task_tool_association
import leodb.models.account.tool_use_spec
import leodb.models.general.user
import leodb.models.general.user_themes
import leodb.models.general.user_theme_indicator
import leodb.models.general.user_invitation
import leodb.models.general.user_preferences
import leodb.models.general.user_session
import leodb.models.general.account_data_connection


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the sqlalchemy.url from our centralized settings object
# This ensures migrations use the same database URL as the application
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_object(object, name, type_, reflected, compare_to):
    """
    Should you include this table or not?
    """
    if type_ == "table":
        return object.schema == settings.POSTGRES_GENERAL_SCHEMA
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        version_table_schema=settings.POSTGRES_GENERAL_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        version_table_schema=settings.POSTGRES_GENERAL_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


from leodb.core.connection_manager import connection_manager

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Use the default engine from our connection manager
    engine = await connection_manager.get_engine()

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
