import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any, Union

import asyncpg
import logfire
from annotated_types import MinLen
from devtools import debug
from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.format_as_xml import format_as_xml

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_asyncpg()

DB_SCHEMA = """
CREATE TABLE models (
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT,
        contributors TEXT[],
        reference_links TEXT[],
        permanent_url TEXT,
        associated_publication TEXT,
        tags TEXT[],
        framework TEXT,
        programming_language TEXT,
        is_marked_spam BOOLEAN,
        last_modified TIMESTAMP,
        peer_reviewed BOOLEAN,
        featured BOOLEAN,
        is_replication BOOLEAN,
        live BOOLEAN,
        first_published_at TIMESTAMP,
        last_published_on TIMESTAMP,
        downloads INTEGER
    );
"""
SQL_EXAMPLES = [
    {
        'request': 'show me featured models about epidemiology with more than 500 downloads',
        'response': "SELECT * FROM models WHERE featured = TRUE AND 'epidemiology' = ANY(tags) AND downloads > 500",
    },
    {
        'request': 'find peer-reviewed Python models published in the last year',
        'response': "SELECT * FROM models WHERE peer_reviewed = TRUE AND programming_language = 'Python' AND first_published_at > CURRENT_DATE - INTERVAL '1 year'",
    },
    {
        'request': 'show me models with at least 3 contributors that use Mesa framework',
        'response': "SELECT * FROM models WHERE array_length(contributors, 1) >= 3 AND framework = 'Mesa'",
    },
    {
        'request': 'find live models that are replications and have an associated publication',
        'response': "SELECT * FROM models WHERE live = TRUE AND is_replication = TRUE AND associated_publication IS NOT NULL",
    },
    {
        'request': 'show me models modified in 2024 that are either featured or peer-reviewed',
        'response': "SELECT * FROM models WHERE EXTRACT(YEAR FROM last_modified) = 2024 AND (featured = TRUE OR peer_reviewed = TRUE)",
    }
]



@dataclass
class Deps:
    conn: asyncpg.Connection


class Success(BaseModel):
    """Response when SQL could be successfully generated."""

    sql_query: Annotated[str, MinLen(1)]
    explanation: str = Field(
        '', description='Explanation of the SQL query, as markdown'
    )


class InvalidRequest(BaseModel):
    """Response the user input didn't include enough information to generate SQL."""

    error_message: str


Response: TypeAlias = Union[Success, InvalidRequest]
agent: Agent[Deps, Response] = Agent(
    'ollama:llama3.1',
    # 'google-gla:gemini-1.5-flash',
    # Type ignore while we wait for PEP-0747, nonetheless unions will work fine everywhere else
    result_type=Response,  # type: ignore
    deps_type=Deps,
    retries=5
)


@agent.system_prompt
async def system_prompt() -> str:
    return f"""\
Given the following PostgreSQL table of records, your job is to
write a SQL query that suits the user's request.

Database schema:

{DB_SCHEMA}

today's date = {date.today()}

{format_as_xml(SQL_EXAMPLES)}
"""


@agent.result_validator
async def validate_result(ctx: RunContext[Deps], result: Response) -> Response:
    if isinstance(result, InvalidRequest):
        return result

    # gemini often adds extraneous backslashes to SQL
    result.sql_query = result.sql_query.replace('\\', '')
    if not result.sql_query.upper().startswith('SELECT'):
        raise ModelRetry('Please create a SELECT query')

    try:
        await ctx.deps.conn.execute(f'EXPLAIN {result.sql_query}')
    except asyncpg.exceptions.PostgresError as e:
        raise ModelRetry(f'Invalid query: {e}') from e
    else:
        return result


async def main():
    if len(sys.argv) == 1:
        prompt = 'select models to which Christopher contributed'
    else:
        prompt = sys.argv[1]

    async with database_connect(
        'postgresql://postgres:postgres@localhost:54320', 'comses_metadata_fake_db'
    ) as conn:
        deps = Deps(conn)
        result = await agent.run(prompt, deps=deps)
    debug(result.data)


# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
@asynccontextmanager
async def database_connect(server_dsn: str, database: str) -> AsyncGenerator[Any, None]:
    with logfire.span('check and create DB'):
        conn = await asyncpg.connect(server_dsn)
        try:
            db_exists = await conn.fetchval(
                'SELECT 1 FROM pg_database WHERE datname = $1', database
            )
            if not db_exists:
                await conn.execute(f'CREATE DATABASE {database}')
        finally:
            await conn.close()

    conn = await asyncpg.connect(f'{server_dsn}/{database}')
    try:
        # with logfire.span('create schema'):
        #     async with conn.transaction():
        #         if not db_exists:
        #             await conn.execute(
        #                 "CREATE TYPE log_level AS ENUM ('debug', 'info', 'warning', 'error', 'critical')"
        #             )
        #         await conn.execute(DB_SCHEMA)
        yield conn
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())