"""設定管理モジュール"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# デフォルト設定
DEFAULT_JOURNAL_DIR = Path(
    os.getenv("ORGJOURNAL_DIR", str(Path.home() / "Documents" / "org" / "p1-journal"))
)
DEFAULT_LAST_DAYS = 7

# ジャーナルファイル名パターン
JOURNAL_FILE_PATTERN = "journal-{year_month}.org"

def get_journal_dir() -> Path:
    """ジャーナルディレクトリのパスを取得"""
    return DEFAULT_JOURNAL_DIR
