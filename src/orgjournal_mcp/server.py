"""FastMCP サーバー実装"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .converter import convert_to_json_schema, search_entries
from .config import DEFAULT_JOURNAL_DIR, DEFAULT_LAST_DAYS

# FastMCP サーバーインスタンスを作成
mcp = FastMCP("orgjournal-mcp")


@mcp.tool()
def get_journal_entries(
    last_days: Optional[int] = None,
    since: Optional[str] = None,
    before: Optional[str] = None,
    journal_dir: Optional[str] = None
) -> dict:
    """
    Retrieve journal entries for a specified date range.

    Args:
        last_days: Get entries from the last N days (e.g., 7, 30, 90)
        since: Get entries from this date onwards (YYYY-MM-DD format)
        before: Get entries before this date (YYYY-MM-DD format)
        journal_dir: Path to the journal directory (defaults to default directory if omitted)

    Returns:
        Dictionary containing a list of journal entries

    Examples:
        - get_journal_entries(last_days=7)  # Last 7 days
        - get_journal_entries(since="2025-01-01")  # From January 1, 2025 onwards
        - get_journal_entries(since="2025-01-01", before="2025-02-01")  # January 2025
    """
    # 日付文字列をdatetimeオブジェクトに変換
    since_dt = datetime.fromisoformat(since) if since else None
    before_dt = datetime.fromisoformat(before) if before else None

    # ジャーナルディレクトリ
    journal_path = Path(journal_dir) if journal_dir else DEFAULT_JOURNAL_DIR

    # エントリーを取得
    result = convert_to_json_schema(
        journal_dir=journal_path,
        last_days=last_days,
        since=since_dt,
        before=before_dt
    )

    return {
        "entries": result["entries"],
        "count": len(result["entries"]),
        "period": {
            "last_days": last_days,
            "since": since,
            "before": before
        }
    }


@mcp.tool()
def search_journal(
    query: str,
    last_days: Optional[int] = None,
    since: Optional[str] = None,
    before: Optional[str] = None,
    search_in_body: bool = True,
    search_in_title: bool = True,
    search_in_tags: bool = True,
    journal_dir: Optional[str] = None
) -> dict:
    """
    Search journals by keyword.

    Args:
        query: Search keyword
        last_days: Search period (last N days)
        since: Start date of search period (YYYY-MM-DD format)
        before: End date of search period (YYYY-MM-DD format)
        search_in_body: Whether to include body in search
        search_in_title: Whether to include title in search
        search_in_tags: Whether to include tags in search
        journal_dir: Path to the journal directory (defaults to default directory if omitted)

    Returns:
        Dictionary containing list of search result entries

    Examples:
        - search_journal("meeting", last_days=30)  # Search for "meeting" in the last 30 days
        - search_journal("project", search_in_tags=True)  # Search in tags
    """
    # 日付文字列をdatetimeオブジェクトに変換
    since_dt = datetime.fromisoformat(since) if since else None
    before_dt = datetime.fromisoformat(before) if before else None

    # ジャーナルディレクトリ
    journal_path = Path(journal_dir) if journal_dir else DEFAULT_JOURNAL_DIR

    # まずエントリーを取得
    result = convert_to_json_schema(
        journal_dir=journal_path,
        last_days=last_days,
        since=since_dt,
        before=before_dt
    )

    # 検索を実行
    search_results = search_entries(
        entries=result["entries"],
        query=query,
        search_in_body=search_in_body,
        search_in_title=search_in_title,
        search_in_tags=search_in_tags
    )

    return {
        "entries": search_results,
        "count": len(search_results),
        "query": query,
        "search_options": {
            "search_in_body": search_in_body,
            "search_in_title": search_in_title,
            "search_in_tags": search_in_tags
        }
    }


@mcp.tool()
def get_recent_entries(
    days: int = DEFAULT_LAST_DAYS,
    journal_dir: Optional[str] = None
) -> dict:
    """
    Get entries from the last N days (simplified version).

    Args:
        days: Number of days to retrieve (default: 7 days)
        journal_dir: Path to the journal directory (defaults to default directory if omitted)

    Returns:
        Dictionary containing a list of journal entries

    Examples:
        - get_recent_entries()  # Last 7 days
        - get_recent_entries(days=30)  # Last 30 days
    """
    # ジャーナルディレクトリ
    journal_path = Path(journal_dir) if journal_dir else DEFAULT_JOURNAL_DIR

    # エントリーを取得
    result = convert_to_json_schema(
        journal_dir=journal_path,
        last_days=days
    )

    return {
        "entries": result["entries"],
        "count": len(result["entries"]),
        "days": days
    }


def run_server():
    """MCPサーバーを起動"""
    mcp.run()
