import typer
from mcp.server.fastmcp import FastMCP

from .mcptools import DateTimeMCPTools
from .clioptions import LogLevelOption, MCPAddressOption, MCPPortOption, MCPTransportOption


app = typer.Typer(no_args_is_help=True)


@app.command(help="Starts an MCP server with date and time tools.")
def mcp(
    log_level: LogLevelOption = 'INFO',
    mcp_address: MCPAddressOption = '0.0.0.0',
    mcp_port: MCPPortOption = 8049,
    mcp_transport: MCPTransportOption = 'stdio',
) -> None:
    """
    Starts an MCP server with date and time tools.
    """
    params = {}
    if mcp_transport == 'sse':
        params['host'] = mcp_address
        params['port'] = mcp_port
    server = FastMCP('MCP Server with datetime tools', '0.1.0', log_level=log_level, **params)
    date_time_tools = DateTimeMCPTools()
    date_time_tools.register_tools(server)
    server.run(transport=mcp_transport)
