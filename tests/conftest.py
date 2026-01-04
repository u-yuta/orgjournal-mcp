"""
共通テストフィクスチャ
"""

from pathlib import Path
from datetime import datetime
import pytest
from typing import Dict, List


@pytest.fixture
def fixtures_dir() -> Path:
    """テストフィクスチャディレクトリのパスを返す"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_journal_2025_01(fixtures_dir: Path) -> Path:
    """2025年1月のサンプルジャーナルファイルパス"""
    return fixtures_dir / "sample_journal_2025-01.org"


@pytest.fixture
def sample_journal_2024_12(fixtures_dir: Path) -> Path:
    """2024年12月のサンプルジャーナルファイルパス"""
    return fixtures_dir / "sample_journal_2024-12.org"


@pytest.fixture
def empty_journal(fixtures_dir: Path) -> Path:
    """空のジャーナルファイルパス"""
    return fixtures_dir / "empty_journal.org"


@pytest.fixture
def sample_entries_data() -> List[Dict]:
    """テスト用のサンプルエントリーデータ"""
    return [
        {
            "date": "2025-01-04",
            "day_of_week": "Saturday",
            "timestamp": "2025-01-04T09:00:00",
            "title": "Project Meeting",
            "body": "Discussed new features in today's project meeting.",
            "tags": ["meeting", "work"]
        },
        {
            "date": "2025-01-04",
            "day_of_week": "Saturday",
            "timestamp": "2025-01-04T14:30:00",
            "title": "Code Review",
            "body": "Reviewed pull requests for the authentication module.",
            "tags": ["code", "review"]
        },
        {
            "date": "2025-01-03",
            "day_of_week": "Friday",
            "timestamp": "2025-01-03T10:00:00",
            "title": "Daily Standup",
            "body": "Team standup meeting.",
            "tags": ["meeting"]
        },
        {
            "date": "2025-01-03",
            "day_of_week": "Friday",
            "timestamp": "2025-01-03T16:00:00",
            "title": "Personal Note",
            "body": "Some personal thoughts about the project.",
            "tags": []
        }
    ]
