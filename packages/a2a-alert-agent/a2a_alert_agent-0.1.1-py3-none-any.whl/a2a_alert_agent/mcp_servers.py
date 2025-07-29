"""MCP servers."""

from typing import Any

from a2a_alert_agent.setting import system_mcp_server_settings

ZMP_ALERT_OPENAPI_MCP_SERVER = {
    "zmp-alert-mcp-server": {
        "transport": "streamable_http",
        "url": "http://zmp-alert-openapi-mcp-server.aiops:20000/mcp",
    }
}

ZMP_CICD_OPENAPI_MCP_SERVER = {
    "zmp-cicd-mcp-server": {
        "transport": "streamable_http",
        "url": "http://zmp-cicd-openapi-mcp-server.aiops:20001/mcp",
    }
}

ZMP_MCM_OPENAPI_MCP_SERVER = {
    "zmp-mcm-mcp-server": {
        "transport": "streamable_http",
        "url": "http://zmp-mcm-openapi-mcp-server.aiops:20002/mcp",
    }
}

ZMP_CORE_OPENAPI_MCP_SERVER = {
    "zmp-core-mcp-server": {
        "transport": "streamable_http",
        "url": "http://zmp-core-openapi-mcp-server.aiops:20003/mcp",
    }
}

ZMP_LOGGING_OPENAPI_MCP_SERVER = {
    "zmp-logging-mcp-server": {
        "transport": "streamable_http",
        "url": "http://zmp-logging-openapi-mcp-server.aiops:20004/mcp",
    }
}

ZMP_METRIC_CHART_GENERATOR_MCP_SERVER = {
    "zmp-chart-mcp-server": {
        "transport": "streamable_http",
        "url": "http://zmp-metric-chart-generator-mcp-server.aiops:20099/mcp",
    }
}

FILE_SYSTEM_MCP_SERVER = {
    "file-system-mcp-server": {
        "transport": "stdio",
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            system_mcp_server_settings.file_system_root_path,
        ],
    }
}

SLACK_MCP_SERVER = {
    "slack-mcp-server": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "env": {
            "SLACK_BOT_TOKEN": system_mcp_server_settings.slack_bot_token,
            "SLACK_TEAM_ID": system_mcp_server_settings.slack_team_id,
        },
    }
}

zmp_default_mcp_servers: dict[str, Any] = {
    **ZMP_ALERT_OPENAPI_MCP_SERVER,
    **ZMP_CICD_OPENAPI_MCP_SERVER,
    **ZMP_MCM_OPENAPI_MCP_SERVER,
    **ZMP_CORE_OPENAPI_MCP_SERVER,
    **ZMP_LOGGING_OPENAPI_MCP_SERVER,
    **ZMP_METRIC_CHART_GENERATOR_MCP_SERVER,
    **FILE_SYSTEM_MCP_SERVER,
    **SLACK_MCP_SERVER,
}


def is_system_default_mcp_server(mcp_server_name: str) -> bool:
    """Check if the MCP server is a system default MCP server."""
    for server_name, _ in zmp_default_mcp_servers.items():
        if server_name == mcp_server_name:
            return True
    return False
