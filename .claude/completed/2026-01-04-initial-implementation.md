# 目的

Journalファイルの内容をLLMが利用できるようにするためのMCPサーバーを提供する。

journalファイルが月別に別れている（フォルダは ~/Documents/org/p1-journal/ 。ファイル名は journal-2025-01.org journal-2025-02.org journal-2025-03.org journal-2025-04.org journal-2025-05.org journal-2025-06.org journal-2025-07.org journal-2025-08.org journal-2025-09.org journal-2025-10.org journal-2025-11.org journal-2025-12.org journal-2026-01.org）。

# Journal の読み込み機能

日付範囲に応じて必要なファイルを自動的に読み込む。

```python
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from orgparse import load
import re

# デフォルト設定
DEFAULT_JOURNAL_DIR = Path.home() / "Documents" / "org" / "p1-journal"
DEFAULT_LAST_DAYS = 7

def remove_timestamp(heading):
    """見出しからタイムスタンプを除去"""
    return re.sub(r'\[[\d\-]+ \w+ [\d:]+\]\s*', '', heading)

def extract_tags(heading):
    """見出しからタグを抽出"""
    tag_match = re.search(r':([^:]+):$', heading)
    if tag_match:
        tags = tag_match.group(1).split(':')
        return [tag for tag in tags if tag]
    return []

def remove_tags(heading):
    """見出しからタグを除去"""
    return re.sub(r'\s*:[^:]+:$', '', heading)

def parse_date(date_string):
    """日付文字列をdatetimeオブジェクトに変換"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"無効な日付形式です: {date_string}. YYYY-MM-DD形式で指定してください。")

def get_date_range(last_days=None, since=None, before=None):
    """フィルタリング条件から実際の日付範囲を計算"""
    now = datetime.now()
    
    # デフォルトは直近7日間
    if last_days is None and since is None and before is None:
        last_days = DEFAULT_LAST_DAYS
    
    # 開始日の決定
    if last_days is not None:
        start_date = now - timedelta(days=last_days)
    elif since is not None:
        start_date = since
    else:
        # beforeのみ指定の場合は、十分に古い日付から
        start_date = datetime(2020, 1, 1)
    
    # 終了日の決定
    if before is not None:
        end_date = before
    else:
        end_date = now + timedelta(days=1)  # 今日を含める
    
    return start_date, end_date

def get_required_journal_files(journal_dir, start_date, end_date):
    """日付範囲に必要なジャーナルファイルのリストを取得"""
    required_files = []
    
    # 月ごとにループ
    current = start_date.replace(day=1)
    end = end_date.replace(day=1)
    
    while current <= end:
        year_month = current.strftime('%Y-%m')
        filename = f"journal-{year_month}.org"
        filepath = journal_dir / filename
        
        if filepath.exists():
            required_files.append(filepath)
        
        # 次の月へ
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    return required_files

def filter_entries_by_date(entries, last_days=None, since=None, before=None):
    """日付範囲でエントリーをフィルタリング"""
    if not entries:
        return entries
    
    filtered = entries
    
    # 直近n日間でフィルタリング
    if last_days is not None:
        cutoff_date = datetime.now() - timedelta(days=last_days)
        filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= cutoff_date]
    
    # 指定日以降でフィルタリング
    if since is not None:
        filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) >= since]
    
    # 指定日より前でフィルタリング
    if before is not None:
        filtered = [e for e in filtered if datetime.fromisoformat(e['timestamp']) < before]
    
    return filtered

def process_org_file(org_file_path):
    """単一のOrg-modeファイルを処理してエントリーのリストを返す"""
    try:
        root = load(org_file_path)
        entries = []
        
        for node in root[1:]:
            if node.level == 4:
                # タイムスタンプの取得
                if node.datelist and len(node.datelist) > 0:
                    timestamp = node.datelist[0].start
                else:
                    continue  # タイムスタンプがない場合はスキップ
                
                # 見出しの処理
                heading = remove_timestamp(node.heading)
                tags = extract_tags(heading)
                title = remove_tags(heading).strip()
                
                # 本文の処理
                body = node.body.strip() if node.body else ""
                
                # 日付と曜日の取得
                date_str = timestamp.strftime('%Y-%m-%d')
                day_of_week = timestamp.strftime('%A')
                timestamp_str = timestamp.isoformat()
                
                entry = {
                    "date": date_str,
                    "day_of_week": day_of_week,
                    "timestamp": timestamp_str,
                    "title": title,
                    "body": body,
                    "tags": tags
                }
                
                entries.append(entry)
        
        return entries
    
    except Exception as e:
        print(f"警告: {org_file_path} の処理中に問題が発生しました: {e}", flush=True)
        return []

def convert_to_json_schema(journal_dir, last_days=None, since=None, before=None, verbose=False):
    """ジャーナルディレクトリからJSONスキーマに変換"""
    # 日付範囲を計算
    start_date, end_date = get_date_range(last_days, since, before)
    
    if verbose:
        print(f"検索期間: {start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')}", flush=True)
    
    # 必要なファイルを取得
    required_files = get_required_journal_files(journal_dir, start_date, end_date)
    
    if verbose:
        print(f"読み込むファイル: {len(required_files)}件", flush=True)
        for f in required_files:
            print(f"  - {f.name}", flush=True)
    
    if not required_files:
        print(f"警告: {journal_dir} に該当するジャーナルファイルが見つかりませんでした", flush=True)
    
    all_entries = []
    
    for file_path in required_files:
        entries = process_org_file(file_path)
        all_entries.extend(entries)
    
    # タイムスタンプでソート
    all_entries.sort(key=lambda x: x['timestamp'])
    
    # 日付範囲でフィルタリング
    filtered_entries = filter_entries_by_date(all_entries, last_days, since, before)
    
    return {"entries": filtered_entries}

def main():
    parser = argparse.ArgumentParser(
        description='Org-modeジャーナルファイルをJSONに変換します',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
使用例:
  # 直近7日間（デフォルト）
  %(prog)s
  
  # 直近30日間
  %(prog)s --last-days 30
  
  # 2025年1月1日以降
  %(prog)s --since 2025-01-01
  
  # 2025年2月1日より前
  %(prog)s --before 2025-02-01
  
  # 2025年1月のみ（組み合わせ）
  %(prog)s --since 2025-01-01 --before 2025-02-01
  
  # 直近7日間をファイルに出力
  %(prog)s -o recent.json
  
  # カスタムディレクトリを指定
  %(prog)s --dir /path/to/journal

デフォルトディレクトリ: {DEFAULT_JOURNAL_DIR}
デフォルト日数: {DEFAULT_LAST_DAYS}日
        '''
    )
    
    parser.add_argument(
        '--dir',
        type=Path,
        default=DEFAULT_JOURNAL_DIR,
        help=f'ジャーナルファイルのディレクトリ（デフォルト: {DEFAULT_JOURNAL_DIR}）'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='出力するJSONファイル名（指定しない場合は標準出力）',
        default=None
    )
    
    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='JSONのインデント幅（デフォルト: 2）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='詳細な処理情報を表示'
    )
    
    # 日付範囲フィルタリングオプション
    date_group = parser.add_argument_group('日付範囲フィルタリング')
    
    date_group.add_argument(
        '--last-days',
        type=int,
        metavar='N',
        help=f'直近N日間のエントリーのみを出力（デフォルト: {DEFAULT_LAST_DAYS}）'
    )
    
    date_group.add_argument(
        '--since',
        type=parse_date,
        metavar='YYYY-MM-DD',
        help='指定した日付以降のエントリーのみを出力'
    )
    
    date_group.add_argument(
        '--before',
        type=parse_date,
        metavar='YYYY-MM-DD',
        help='指定した日付より前のエントリーのみを出力'
    )
    
    args = parser.parse_args()
    
    # ディレクトリの存在確認
    if not args.dir.exists():
        print(f"エラー: ディレクトリが存在しません: {args.dir}")
        return 1
    
    if not args.dir.is_dir():
        print(f"エラー: 指定されたパスはディレクトリではありません: {args.dir}")
        return 1
    
    # 変換
    result = convert_to_json_schema(
        args.dir,
        last_days=args.last_days,
        since=args.since,
        before=args.before,
        verbose=args.verbose
    )
    
    # JSON文字列を生成
    json_output = json.dumps(result, ensure_ascii=False, indent=args.indent)
    
    # 出力
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"JSON出力を {args.output} に保存しました")
        print(f"エントリー数: {len(result['entries'])}")
        if result['entries']:
            print(f"期間: {result['entries'][0]['date']} ～ {result['entries'][-1]['date']}")
    else:
        print(json_output)
    
    return 0

if __name__ == "__main__":
    exit(main())
```

**主な変更点:**

1. **ファイル指定不要**: コマンドライン引数からファイル指定を削除
2. **自動ファイル検出**: `get_required_journal_files()`で日付範囲から必要な月のファイルを自動判定
3. **デフォルト動作**: オプション未指定時は直近7日間を処理
4. **ディレクトリ指定**: `--dir`オプションでジャーナルディレクトリをカスタマイズ可能
5. **詳細表示**: `-v`オプションで処理対象ファイルを表示

**使用例:**

```bash
# 直近7日間（デフォルト）
python convert_journal.py

# 直近30日間
python convert_journal.py --last-days 30

# 直近90日間をファイルに保存
python convert_journal.py --last-days 90 -o last_90days.json

# 2025年全体
python convert_journal.py --since 2025-01-01 --before 2026-01-01

# 2025年12月のみ
python convert_journal.py --since 2025-12-01 --before 2026-01-01

# 詳細表示付き
python convert_journal.py --last-days 14 -v

# カスタムディレクトリ
python convert_journal.py --dir /path/to/other/journal --last-days 30
```

これで、日付範囲を指定するだけで必要なファイルが自動的に読み込まれるようになりました。

# パッケージ名とファイル構成
## パッケージ名

**`orgjournal-mcp`**

理由：
- Org-modeのジャーナル機能に特化していることが明確
- MCPサーバーであることが分かりやすい
- PyPIでの命名規則に準拠（ハイフン区切り）

## ファイル構成

```
orgjournal-mcp/
├── pyproject.toml                 # uvで管理するプロジェクト設定
├── uv.lock                        # 依存関係のロックファイル
├── README.md                      # プロジェクトの説明
├── LICENSE                        # ライセンスファイル
├── .gitignore                     # Git除外設定
│
└── src/
    └── orgjournal_mcp/            # メインパッケージ
        ├── __init__.py            # パッケージ初期化
        ├── __main__.py            # CLIエントリーポイント (python -m orgjournal_mcp)
        │
        ├── converter.py           # ジャーナル変換ロジック（convert_journal.pyから移行）
        ├── server.py              # FastMCPサーバー実装
        │
        ├── config.py              # 設定管理（デフォルトパス等）
        └── cli.py                 # CLIコマンド実装
```

## 各ファイルの役割

### `pyproject.toml`
プロジェクトメタデータ、依存関係、ビルド設定

### `src/orgjournal_mcp/__init__.py`
パッケージのバージョン情報とエクスポート

### `src/orgjournal_mcp/converter.py`
- `convert_journal.py`の変換ロジックを移行
- 関数として再利用可能な形に整理
- CLIとMCPサーバーの両方から利用

### `src/orgjournal_mcp/server.py`
- FastMCPを使ったMCPサーバー実装
- `converter.py`の関数を呼び出してツールを提供

### `src/orgjournal_mcp/config.py`
- デフォルトのジャーナルディレクトリパス
- 設定の管理

### `src/orgjournal_mcp/cli.py`
- CLIコマンドの実装（元の`convert_journal.py`のmain関数）
- `converter.py`を利用

### `src/orgjournal_mcp/__main__.py`
- `python -m orgjournal_mcp`で実行可能にする
- CLIとサーバーの起動を切り替え

## 提供するコマンド例

```bash
# CLIとして使用（ジャーナル変換）
uv run orgjournal convert --last-days 7 -o output.json

# MCPサーバーとして起動
uv run orgjournal serve

# または
python -m orgjournal_mcp serve
```

## MCPサーバーが提供するツール（予定）

1. **`get_journal_entries`**: 日付範囲を指定してジャーナルエントリーを取得
2. **`search_journal`**: キーワードでジャーナルを検索
3. **`get_recent_entries`**: 直近N日間のエントリーを取得
