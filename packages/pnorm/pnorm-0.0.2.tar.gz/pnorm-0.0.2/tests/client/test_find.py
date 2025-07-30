import psycopg
import pytest
import pytest_asyncio
from pydantic import BaseModel

from pnorm import QueryContext
from pnorm.hooks.opentelemetry import SpanHook
from tests.fixutres.client_counter import (  # noqa: F401
    PostgresClientCounter,
    client,
)
from tests.utils.telemetry import assert_span

pytest_plugins = ("pytest_asyncio",)


class TestAsyncFind:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_tests(self, client: PostgresClientCounter) -> None: # noqa: F811
        async with client.start_session() as session:
            await session.execute(
                "create table if not exists pnorm__async_find__tests (user_id int unique, name text)"
            )
            await session.execute(
                "insert into pnorm__async_find__tests (user_id, name) values (1, 'test') on conflict do nothing"
            )
            await session.execute(
                "insert into pnorm__async_find__tests (user_id, name) values (3, 'test') on conflict do nothing"
            )

    @pytest.mark.asyncio
    async def test_no_records(self, client: PostgresClientCounter) -> None: # noqa: F811
        with assert_span(
            {
                "attributes": {
                    "db.system.name": "postgresql",
                    "db.collection.name": "pnorm__async_find__tests",
                    "db.operation.name": "SELECT",
                    "db.query.summary": "get from pnorm__async_find__tests",
                    "db.query.text": "select * from pnorm__async_find__tests where user_id = %(user_id)s",
                    "db.operation.parameter.user_id": 2,
                    # "server.address": "localhost",
                    # "server.port": 5434,
                    # "network.peer.address": "localhost",
                    # "network.peer.port": 5434,
                    "db.operation.batch.size": 1,
                    "db.response.returned_rows": 0,
                }
            }
        ):
            res = await client.find(
                dict,
                "select * from pnorm__async_find__tests where user_id = %(user_id)s",
                {"user_id": 2},
                query_context=QueryContext(
                    primary_table_name="pnorm__async_find__tests",
                    operation_name="SELECT",
                    query_summary="get from pnorm__async_find__tests",
                ),
                hooks=[SpanHook()],
            )

            assert res is None

    @pytest.mark.asyncio
    async def test_one_record(self, client: PostgresClientCounter) -> None: # noqa: F811
        with assert_span(
            {
                "attributes": {
                    "db.system.name": "postgresql",
                    "db.collection.name": "pnorm__async_find__tests",
                    "db.operation.name": "SELECT",
                    "db.query.summary": "get from pnorm__async_find__tests",
                    "db.query.text": "select * from pnorm__async_find__tests where user_id = %(user_id)s",
                    "db.operation.parameter.user_id": 1,
                    # "server.address": "localhost",
                    # "server.port": 5434,
                    # "network.peer.address": "localhost",
                    # "network.peer.port": 5434,
                    "db.operation.batch.size": 1,
                    "db.response.returned_rows": 1,
                }
            }
        ):
            res = await client.find(
                dict,
                "select * from pnorm__async_find__tests where user_id = %(user_id)s",
                {"user_id": 1},
                query_context=QueryContext(
                    primary_table_name="pnorm__async_find__tests",
                    operation_name="SELECT",
                    query_summary="get from pnorm__async_find__tests",
                ),
                hooks=[SpanHook()],
            )

            assert res is not None

    @pytest.mark.asyncio
    async def test_multiple_records(self, client: PostgresClientCounter) -> None: # noqa: F811
        with assert_span(
            {
                "attributes": {
                    "db.system.name": "postgresql",
                    "db.collection.name": "pnorm__async_find__tests",
                    "db.operation.name": "SELECT",
                    "db.query.summary": "get from pnorm__async_find__tests",
                    "db.query.text": "select * from pnorm__async_find__tests order by user_id asc",
                    # "server.address": "localhost",
                    # "server.port": 5434,
                    # "network.peer.address": "localhost",
                    # "network.peer.port": 5434,
                    "db.operation.batch.size": 1,
                    "db.response.returned_rows": 1,
                }
            }
        ):
            res = await client.find(
                dict,
                "select * from pnorm__async_find__tests order by user_id asc",
                query_context=QueryContext(
                    primary_table_name="pnorm__async_find__tests",
                    operation_name="SELECT",
                    query_summary="get from pnorm__async_find__tests",
                ),
                hooks=[SpanHook()],
            )

            assert res is not None
            assert res["user_id"] == 1

    @pytest.mark.asyncio
    async def test_dict(self, client: PostgresClientCounter) -> None: # noqa: F811
        res = await client.find(
            dict,
            "select * from pnorm__async_find__tests where user_id = %(user_id)s",
            {"user_id": 1},
            query_context=QueryContext(
                primary_table_name="pnorm__async_find__tests",
                operation_name="SELECT",
                query_summary="get from pnorm__async_find__tests",
            ),
        )

        assert res == {"user_id": 1, "name": "test"}

    @pytest.mark.asyncio
    async def test_pydantic(self, client: PostgresClientCounter) -> None: # noqa: F811
        class ResponseModel(BaseModel):
            user_id: int
            name: str

        res = await client.find(
            ResponseModel,
            "select * from pnorm__async_find__tests where user_id = %(user_id)s",
            {"user_id": 1},
            query_context=QueryContext(
                primary_table_name="pnorm__async_find__tests",
                operation_name="SELECT",
                query_summary="get from pnorm__async_find__tests",
            ),
        )

        assert res == ResponseModel(user_id=1, name="test")

    @pytest.mark.asyncio
    async def test_no_records_default(self, client: PostgresClientCounter) -> None: # noqa: F811
        res = await client.find(
            dict,
            "select * from pnorm__async_find__tests where user_id = %(user_id)s",
            {"user_id": 2},
            default={"user_id": 0, "name": "default"},
            query_context=QueryContext(
                primary_table_name="pnorm__async_find__tests",
                operation_name="SELECT",
                query_summary="get from pnorm__async_find__tests",
            ),
        )

        assert res == {"user_id": 0, "name": "default"}

    @pytest.mark.asyncio
    async def test_combine_into_return_model(
        self,
        client: PostgresClientCounter, # noqa: F811
    ) -> None:
        res = await client.find(
            dict,
            "select name from pnorm__async_find__tests where user_id = %(user_id)s",
            {"user_id": 1},
            combine_into_return_model=True,
            query_context=QueryContext(
                primary_table_name="pnorm__async_find__tests",
                operation_name="SELECT",
                query_summary="get from pnorm__async_find__tests",
            ),
        )

        assert res == {"user_id": 1, "name": "test"}

    @pytest.mark.asyncio
    async def test_db_timeout(self, client: PostgresClientCounter) -> None: # noqa: F811
        ...

    @pytest.mark.asyncio
    async def test_sql_error(self, client: PostgresClientCounter) -> None: # noqa: F811
        try:
            await client.find(
                dict,
                "select * from pnorm__async_find__tests where user_id == %(user_id)s",
                {"user_id": 2},
                query_context=QueryContext(
                    primary_table_name="pnorm__async_find__tests",
                    operation_name="SELECT",
                    query_summary="get from pnorm__async_find__tests",
                ),
            )
            raise AssertionError("psycopg.errors.UndefinedFunction not raised")
        except psycopg.errors.UndefinedFunction:
            ...
        except Exception:
            raise AssertionError("Unexpected exception")

    @pytest.mark.asyncio
    async def test_type_error(self, client: PostgresClientCounter) -> None: # noqa: F811
        try:
            await client.find(
                dict,
                "select * from pnorm__async_find__tests where user_id = %(user_id)s",
                {"user_id": "hello"},
                query_context=QueryContext(
                    primary_table_name="pnorm__async_find__tests",
                    operation_name="SELECT",
                    query_summary="get from pnorm__async_find__tests",
                ),
            )
            raise AssertionError("psycopg.errors.UndefinedFunction not raised")
        except psycopg.errors.UndefinedFunction:
            ...
        except Exception:
            ...

    @pytest.mark.asyncio
    async def test_params_dict(self, client: PostgresClientCounter) -> None: # noqa: F811
        response = await client.find(
            dict,
            "select * from pnorm__async_find__tests where user_id = %(user_id)s",
            {"user_id": 1},
            query_context=QueryContext(
                primary_table_name="pnorm__async_find__tests",
                operation_name="SELECT",
                query_summary="get from pnorm__async_find__tests",
            ),
        )

        assert response == {"user_id": 1, "name": "test"}

    @pytest.mark.asyncio
    async def test_params_pydantic(self, client: PostgresClientCounter) -> None: # noqa: F811
        class Params(BaseModel):
            user_id: int

        response = await client.find(
            dict,
            "select * from pnorm__async_find__tests where user_id = %(user_id)s",
            Params(user_id=1),
            query_context=QueryContext(
                primary_table_name="pnorm__async_find__tests",
                operation_name="SELECT",
                query_summary="get from pnorm__async_find__tests",
            ),
        )

        assert response == {"user_id": 1, "name": "test"}
