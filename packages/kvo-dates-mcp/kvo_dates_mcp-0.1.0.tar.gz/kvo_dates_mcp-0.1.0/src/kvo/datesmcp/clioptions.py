from typing import Annotated, Literal

import typer
from pydantic import TypeAdapter


LogLevelOption = Annotated[str, typer.Option(
    '--log-level', help="Log level", envvar='LOG_LEVEL'),]



MCPTransportType = Literal['stdio', 'sse']


def parse_mcp_transport(value: str) -> MCPTransportType:
    return TypeAdapter(MCPTransportType).validate_strings(value)


MCPAddressOption = Annotated[str, typer.Option(
    '--mcp-address', help="MCP server address", envvar='MCP_ADDRESS'),]
MCPPortOption = Annotated[int, typer.Option(
    '--mcp-port', help="MCP server port", envvar='MCP_PORT'),]
MCPTransportOption = Annotated[MCPTransportType, typer.Option(
    '--mcp-transport', help="MCP server transport", envvar='MCP_TRANSPORT',
    parser=parse_mcp_transport),]
