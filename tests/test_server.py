"""
server.py のテスト
"""

import pytest
from pathlib import Path
from datetime import datetime

from orgjournal_mcp.server import (
    get_journal_entries,
    search_journal,
    get_recent_entries,
    get_entries_by_tag,
)


class TestGetJournalEntries:
    """get_journal_entries ツールのテスト"""

    def test_get_entries_with_fixtures(self, fixtures_dir: Path):
        """フィクスチャを使ったエントリー取得"""
        result = get_journal_entries(
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        assert "count" in result
        assert "period" in result
        assert isinstance(result["entries"], list)
        assert result["count"] == len(result["entries"])

    def test_get_entries_with_date_range(self, fixtures_dir: Path):
        """日付範囲指定でのエントリー取得"""
        result = get_journal_entries(
            since="2025-01-03",
            before="2025-01-05",
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        assert result["period"]["since"] == "2025-01-03"
        assert result["period"]["before"] == "2025-01-05"

        # フィルタリングされたエントリーの確認
        for entry in result["entries"]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            assert datetime(2025, 1, 3) <= entry_date < datetime(2025, 1, 5)

    def test_get_entries_last_days(self, fixtures_dir: Path):
        """last_days パラメータでのエントリー取得"""
        result = get_journal_entries(
            last_days=7,
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        assert result["period"]["last_days"] == 7

    def test_response_structure(self, fixtures_dir: Path):
        """レスポンス構造の確認"""
        result = get_journal_entries(
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        # トップレベルのキー確認
        assert set(result.keys()) == {"entries", "count", "period"}

        # period の構造確認
        assert "last_days" in result["period"]
        assert "since" in result["period"]
        assert "before" in result["period"]


class TestSearchJournal:
    """search_journal ツールのテスト"""

    def test_search_basic(self, fixtures_dir: Path):
        """基本的なキーワード検索"""
        result = search_journal(
            query="meeting",
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        assert "count" in result
        assert "query" in result
        assert "search_options" in result
        assert result["query"] == "meeting"
        assert result["count"] == len(result["entries"])

    def test_search_in_title_only(self, fixtures_dir: Path):
        """タイトルのみの検索"""
        result = search_journal(
            query="meeting",
            last_days=365,
            search_in_title=True,
            search_in_body=False,
            search_in_tags=False,
            journal_dir=str(fixtures_dir)
        )

        assert result["search_options"]["search_in_title"] is True
        assert result["search_options"]["search_in_body"] is False
        assert result["search_options"]["search_in_tags"] is False

    def test_search_in_tags_only(self, fixtures_dir: Path):
        """タグのみの検索"""
        result = search_journal(
            query="work",
            last_days=365,
            search_in_title=False,
            search_in_body=False,
            search_in_tags=True,
            journal_dir=str(fixtures_dir)
        )

        assert result["search_options"]["search_in_tags"] is True
        # 結果があれば、タグに "work" が含まれていることを確認
        for entry in result["entries"]:
            assert "work" in entry["tags"]

    def test_search_with_date_filter(self, fixtures_dir: Path):
        """日付フィルタリング付きの検索"""
        result = search_journal(
            query="meeting",
            since="2025-01-01",
            before="2025-01-10",
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        # 日付範囲内のエントリーのみが含まれていることを確認
        for entry in result["entries"]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            assert datetime(2025, 1, 1) <= entry_date < datetime(2025, 1, 10)

    def test_search_no_results(self, fixtures_dir: Path):
        """結果なしの検索"""
        result = search_journal(
            query="nonexistent_keyword_xyz",
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert result["entries"] == []
        assert result["count"] == 0

    def test_response_structure(self, fixtures_dir: Path):
        """レスポンス構造の確認"""
        result = search_journal(
            query="test",
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        # トップレベルのキー確認
        assert set(result.keys()) == {"entries", "count", "query", "search_options"}

        # search_options の構造確認
        assert "search_in_body" in result["search_options"]
        assert "search_in_title" in result["search_options"]
        assert "search_in_tags" in result["search_options"]


class TestGetRecentEntries:
    """get_recent_entries ツールのテスト"""

    def test_get_recent_default(self, fixtures_dir: Path):
        """デフォルトパラメータでの取得（choreタグを除外）"""
        result = get_recent_entries(journal_dir=str(fixtures_dir))

        assert "entries" in result
        assert "count" in result
        assert "days" in result
        assert result["days"] == 7  # デフォルト値
        assert result["count"] == len(result["entries"])

        # "chore" タグが除外されていることを確認
        for entry in result["entries"]:
            assert "chore" not in entry["tags"]

    def test_get_recent_custom_days(self, fixtures_dir: Path):
        """カスタム日数での取得"""
        result = get_recent_entries(
            days=30,
            journal_dir=str(fixtures_dir)
        )

        assert result["days"] == 30

        # "chore" タグが除外されていることを確認
        for entry in result["entries"]:
            assert "chore" not in entry["tags"]

    def test_response_structure(self, fixtures_dir: Path):
        """レスポンス構造の確認"""
        result = get_recent_entries(journal_dir=str(fixtures_dir))

        # トップレベルのキー確認
        assert set(result.keys()) == {"entries", "count", "days"}

        # entries が正しい構造を持っているか確認
        if result["entries"]:
            entry = result["entries"][0]
            required_keys = {"date", "day_of_week", "timestamp", "title", "body", "tags"}
            assert all(key in entry for key in required_keys)


class TestGetEntriesByTag:
    """get_entries_by_tag ツールのテスト"""

    def test_get_entries_with_include_tag(self, fixtures_dir: Path):
        """特定のタグを含むエントリーの取得"""
        result = get_entries_by_tag(
            tags=["work"],
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        assert "count" in result
        assert "filter" in result
        assert result["filter"]["include_tags"] == ["work"]
        assert result["count"] == len(result["entries"])

        # 全てのエントリーに "work" タグが含まれていることを確認
        for entry in result["entries"]:
            assert "work" in entry["tags"]

    def test_get_entries_with_exclude_tag(self, fixtures_dir: Path):
        """特定のタグを除外したエントリーの取得"""
        result = get_entries_by_tag(
            exclude_tags=["meeting"],
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        assert result["filter"]["exclude_tags"] == ["meeting"]

        # 全てのエントリーに "meeting" タグが含まれていないことを確認
        for entry in result["entries"]:
            assert "meeting" not in entry["tags"]

    def test_get_entries_default_no_exclude(self, fixtures_dir: Path):
        """デフォルトでタグ除外がないことを確認"""
        result = get_entries_by_tag(
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert result["filter"]["exclude_tags"] is None

    def test_get_entries_include_and_exclude(self, fixtures_dir: Path):
        """includeとexcludeの組み合わせ"""
        result = get_entries_by_tag(
            tags=["work"],
            exclude_tags=["meeting"],
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert result["filter"]["include_tags"] == ["work"]
        assert result["filter"]["exclude_tags"] == ["meeting"]

        # 全てのエントリーに "work" タグが含まれ、"meeting" タグが含まれていないことを確認
        for entry in result["entries"]:
            assert "work" in entry["tags"]
            assert "meeting" not in entry["tags"]

    def test_get_entries_with_empty_exclude(self, fixtures_dir: Path):
        """空のexclude_tagsで全てのタグを含める"""
        result = get_entries_by_tag(
            exclude_tags=[],
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert result["filter"]["exclude_tags"] == []

        # 全てのエントリーが含まれる
        all_entries = get_journal_entries(
            last_days=365,
            journal_dir=str(fixtures_dir)
        )
        assert result["count"] == all_entries["count"]

    def test_get_entries_exclude_chore_explicitly(self, fixtures_dir: Path):
        """明示的に "chore" タグを除外"""
        result = get_entries_by_tag(
            exclude_tags=["chore"],
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        assert result["filter"]["exclude_tags"] == ["chore"]

        # 全てのエントリーに "chore" タグが含まれていないことを確認
        for entry in result["entries"]:
            assert "chore" not in entry["tags"]

    def test_get_entries_with_date_range(self, fixtures_dir: Path):
        """日付範囲指定付きのタグフィルタリング"""
        result = get_entries_by_tag(
            tags=["work"],
            since="2025-01-01",
            before="2025-01-10",
            journal_dir=str(fixtures_dir)
        )

        assert "entries" in result
        # 日付範囲内のエントリーのみが含まれていることを確認
        for entry in result["entries"]:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            assert datetime(2025, 1, 1) <= entry_date < datetime(2025, 1, 10)
            assert "work" in entry["tags"]

    def test_response_structure(self, fixtures_dir: Path):
        """レスポンス構造の確認"""
        result = get_entries_by_tag(
            tags=["work"],
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        # トップレベルのキー確認
        assert set(result.keys()) == {"entries", "count", "filter"}

        # filter の構造確認
        assert "include_tags" in result["filter"]
        assert "exclude_tags" in result["filter"]
        assert "last_days" in result["filter"]
        assert "since" in result["filter"]
        assert "before" in result["filter"]


class TestIntegration:
    """統合テスト"""

    def test_multiple_tools_same_data(self, fixtures_dir: Path):
        """同じデータに対する複数ツールの整合性"""
        # get_journal_entries と get_recent_entries の結果を比較
        # get_recent_entries は "chore" タグを除外するので、
        # get_entries_by_tag で同じフィルターを適用して比較
        entries_with_filter = get_entries_by_tag(
            exclude_tags=["chore"],
            last_days=7,
            journal_dir=str(fixtures_dir)
        )

        recent_result = get_recent_entries(
            days=7,
            journal_dir=str(fixtures_dir)
        )

        # 同じエントリー数を返すはず
        assert entries_with_filter["count"] == recent_result["count"]

    def test_search_subset_of_entries(self, fixtures_dir: Path):
        """検索結果は全エントリーのサブセット"""
        all_entries = get_journal_entries(
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        search_result = search_journal(
            query="meeting",
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        # 検索結果は全エントリー以下のはず
        assert search_result["count"] <= all_entries["count"]

    def test_tag_filter_subset_of_entries(self, fixtures_dir: Path):
        """タグフィルター結果は全エントリーのサブセット"""
        all_entries = get_journal_entries(
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        tag_result = get_entries_by_tag(
            tags=["work"],
            last_days=365,
            journal_dir=str(fixtures_dir)
        )

        # タグフィルター結果は全エントリー以下のはず
        assert tag_result["count"] <= all_entries["count"]
