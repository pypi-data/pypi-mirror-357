import pytest
import pytest_asyncio

from tests.fixutres.client_counter import (
    PostgresClientCounter,
    client,  # noqa: F401
    get_client,
)

pytest_plugins = ("pytest_asyncio",)


class TestConnections:
    @pytest_asyncio.fixture(autouse=True)
    async def setup_tests(self, client: PostgresClientCounter) -> None: # noqa: F811
        async with client.start_session() as session:
            await session.execute(
                "create table if not exists pnorm__connections__tests (user_id int unique, name text)"
            )
            await session.execute(
                "insert into pnorm__connections__tests (user_id, name) values (1, 'test') on conflict do nothing"
            )
            await session.execute(
                "insert into pnorm__connections__tests (user_id, name) values (3, 'test') on conflict do nothing"
            )

    @pytest.mark.asyncio
    async def test_no_session_only_one_connection_get(self) -> None:
        client = get_client() # noqa: F811

        await client.get(
            dict,
            "select * from pnorm__connections__tests where user_id = %(user_id)s",
            {"user_id": 1},
        )

        assert client.check_connections() == 1

    @pytest.mark.asyncio
    async def test_no_session_only_one_connection_find(self) -> None:
        client = get_client() # noqa: F811

        await client.find(
            dict,
            "select * from pnorm__connections__tests where user_id = %(user_id)s",
            {"user_id": 1},
        )

        assert client.check_connections() == 1

    @pytest.mark.asyncio
    async def test_no_session_only_one_connection_select(self) -> None:
        client = get_client() # noqa: F811

        await client.select(
            dict,
            "select * from pnorm__connections__tests where user_id = %(user_id)s",
            {"user_id": 1},
        )

        assert client.check_connections() == 1

    @pytest.mark.asyncio
    async def test_no_session_only_one_connection_execute(self) -> None:
        client = get_client() # noqa: F811

        await client.execute(
            "select * from pnorm__connections__tests where user_id = %(user_id)s",
            {"user_id": 1},
        )

        assert client.check_connections() == 1

    @pytest.mark.asyncio
    async def test_no_session_multiple_connections(self) -> None:
        client = get_client() # noqa: F811

        await client.find(
            dict,
            "select * from pnorm__connections__tests where user_id = %(user_id)s",
            {"user_id": 1},
        )
        await client.find(
            dict,
            "select * from pnorm__connections__tests where user_id = %(user_id)s",
            {"user_id": 2},
        )
        await client.find(
            dict,
            "select * from pnorm__connections__tests where user_id = %(user_id)s",
            {"user_id": 3},
        )

        assert client.check_connections() == 3
