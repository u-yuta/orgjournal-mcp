"""設定管理モジュール"""

from pathlib import Path

# デフォルト設定
DEFAULT_JOURNAL_DIR = Path.home() / "Documents" / "org" / "p1-journal"
DEFAULT_LAST_DAYS = 7

# ジャーナルファイル名パターン
JOURNAL_FILE_PATTERN = "journal-{year_month}.org"

def get_journal_dir() -> Path:
    """ジャーナルディレクトリのパスを取得"""
    return DEFAULT_JOURNAL_DIR
