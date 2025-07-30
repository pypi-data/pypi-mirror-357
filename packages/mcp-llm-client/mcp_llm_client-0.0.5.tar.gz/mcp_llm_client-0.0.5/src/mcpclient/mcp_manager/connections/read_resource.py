from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio


def read_resource(http: str, uri: str) -> any:
    return asyncio.run(async_read_resource(http, uri))


async def async_read_resource(http: str, uri: str):
    async with streamablehttp_client(http) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Read a resource
            resource_result = await session.read_resource(uri)
            return resource_result.contents
