"""orgjournal-mcp: Org-mode ジャーナルファイルを MCP サーバーとして提供"""

__version__ = "0.1.0"

from .server import run_server


def main() -> None:
    """MCPサーバーを起動するメイン関数"""
    run_server()


__all__ = ["main", "run_server", "__version__"]
