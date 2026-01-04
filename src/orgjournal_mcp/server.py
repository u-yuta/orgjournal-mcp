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
    日付範囲を指定してジャーナルエントリーを取得します。

    Args:
        last_days: 直近N日間のエントリーを取得（例: 7, 30, 90）
        since: この日付以降のエントリーを取得（YYYY-MM-DD形式）
        before: この日付より前のエントリーを取得（YYYY-MM-DD形式）
        journal_dir: ジャーナルディレクトリのパス（省略時はデフォルト）

    Returns:
        ジャーナルエントリーのリストを含む辞書

    Examples:
        - get_journal_entries(last_days=7)  # 直近7日間
        - get_journal_entries(since="2025-01-01")  # 2025年1月1日以降
        - get_journal_entries(since="2025-01-01", before="2025-02-01")  # 2025年1月
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
    キーワードでジャーナルを検索します。

    Args:
        query: 検索キーワード
        last_days: 検索対象期間（直近N日間）
        since: 検索対象期間の開始日（YYYY-MM-DD形式）
        before: 検索対象期間の終了日（YYYY-MM-DD形式）
        search_in_body: 本文を検索対象に含めるか
        search_in_title: タイトルを検索対象に含めるか
        search_in_tags: タグを検索対象に含めるか
        journal_dir: ジャーナルディレクトリのパス（省略時はデフォルト）

    Returns:
        検索結果のエントリーリストを含む辞書

    Examples:
        - search_journal("meeting", last_days=30)  # 直近30日間で"meeting"を検索
        - search_journal("project", search_in_tags=True)  # タグで検索
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
    直近N日間のエントリーを取得します（簡易版）。

    Args:
        days: 取得する日数（デフォルト: 7日）
        journal_dir: ジャーナルディレクトリのパス（省略時はデフォルト）

    Returns:
        ジャーナルエントリーのリストを含む辞書

    Examples:
        - get_recent_entries()  # 直近7日間
        - get_recent_entries(days=30)  # 直近30日間
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
