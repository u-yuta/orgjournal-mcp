"""
config.py のテスト
"""

import pytest
from pathlib import Path

from orgjournal_mcp.config import (
    DEFAULT_JOURNAL_DIR,
    DEFAULT_LAST_DAYS,
    JOURNAL_FILE_PATTERN,
    get_journal_dir,
)


class TestConfigConstants:
    """設定定数のテスト"""

    def test_default_journal_dir_type(self):
        """デフォルトジャーナルディレクトリの型確認"""
        assert isinstance(DEFAULT_JOURNAL_DIR, Path)

    def test_default_journal_dir_value(self):
        """デフォルトジャーナルディレクトリの値確認"""
        expected = Path.home() / "Documents" / "org" / "p1-journal"
        assert DEFAULT_JOURNAL_DIR == expected

    def test_default_last_days(self):
        """デフォルト日数の確認"""
        assert DEFAULT_LAST_DAYS == 7
        assert isinstance(DEFAULT_LAST_DAYS, int)

    def test_journal_file_pattern(self):
        """ジャーナルファイルパターンの確認"""
        assert JOURNAL_FILE_PATTERN == "journal-{year_month}.org"
        assert isinstance(JOURNAL_FILE_PATTERN, str)


class TestGetJournalDir:
    """get_journal_dir() 関数のテスト"""

    def test_get_journal_dir_returns_path(self):
        """パスオブジェクトを返すことを確認"""
        result = get_journal_dir()
        assert isinstance(result, Path)

    def test_get_journal_dir_returns_default(self):
        """デフォルト値を返すことを確認"""
        result = get_journal_dir()
        assert result == DEFAULT_JOURNAL_DIR

    def test_get_journal_dir_consistency(self):
        """複数回呼び出しても同じ値を返すことを確認"""
        result1 = get_journal_dir()
        result2 = get_journal_dir()
        assert result1 == result2
