"""ジャーナル変換ロジックモジュール"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from orgparse import load

from .config import DEFAULT_JOURNAL_DIR, DEFAULT_LAST_DAYS


def remove_timestamp(heading: str) -> str:
    """見出しからタイムスタンプを除去"""
    return re.sub(r'\[[\d\-]+ \w+ [\d:]+\]\s*', '', heading)


def extract_tags(heading: str) -> List[str]:
    """見出しからタグを抽出"""
    tag_match = re.search(r':([^:]+):$', heading)
    if tag_match:
        tags = tag_match.group(1).split(':')
        return [tag for tag in tags if tag]
    return []


def remove_tags(heading: str) -> str:
    """見出しからタグを除去"""
    return re.sub(r'\s*:[^:]+:$', '', heading)


def get_date_range(
    last_days: Optional[int] = None,
    since: Optional[datetime] = None,
    before: Optional[datetime] = None
) -> tuple[datetime, datetime]:
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


def get_required_journal_files(
    journal_dir: Path,
    start_date: datetime,
    end_date: datetime
) -> List[Path]:
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


def filter_entries_by_date(
    entries: List[Dict[str, Any]],
    last_days: Optional[int] = None,
    since: Optional[datetime] = None,
    before: Optional[datetime] = None
) -> List[Dict[str, Any]]:
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


def process_org_file(org_file_path: Path) -> List[Dict[str, Any]]:
    """単一のOrg-modeファイルを処理してエントリーのリストを返す"""
    try:
        root = load(str(org_file_path))
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
        # エラーは無視して空のリストを返す
        return []


def convert_to_json_schema(
    journal_dir: Optional[Path] = None,
    last_days: Optional[int] = None,
    since: Optional[datetime] = None,
    before: Optional[datetime] = None
) -> Dict[str, Any]:
    """ジャーナルディレクトリからJSONスキーマに変換"""
    if journal_dir is None:
        journal_dir = DEFAULT_JOURNAL_DIR

    # 日付範囲を計算
    start_date, end_date = get_date_range(last_days, since, before)

    # 必要なファイルを取得
    required_files = get_required_journal_files(journal_dir, start_date, end_date)

    all_entries = []

    for file_path in required_files:
        entries = process_org_file(file_path)
        all_entries.extend(entries)

    # タイムスタンプでソート
    all_entries.sort(key=lambda x: x['timestamp'])

    # 日付範囲でフィルタリング
    filtered_entries = filter_entries_by_date(all_entries, last_days, since, before)

    return {"entries": filtered_entries}


def search_entries(
    entries: List[Dict[str, Any]],
    query: str,
    search_in_body: bool = True,
    search_in_title: bool = True,
    search_in_tags: bool = True
) -> List[Dict[str, Any]]:
    """エントリーをキーワード検索"""
    if not query:
        return entries

    query_lower = query.lower()
    results = []

    for entry in entries:
        matched = False

        if search_in_title and query_lower in entry['title'].lower():
            matched = True

        if search_in_body and query_lower in entry['body'].lower():
            matched = True

        if search_in_tags:
            for tag in entry['tags']:
                if query_lower in tag.lower():
                    matched = True
                    break

        if matched:
            results.append(entry)

    return results


def filter_entries_by_tags(
    entries: List[Dict[str, Any]],
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """エントリーをタグでフィルタリング

    Args:
        entries: フィルタリング対象のエントリーリスト
        include_tags: 含めるタグのリスト（Noneの場合は全て含める）
        exclude_tags: 除外するタグのリスト（Noneの場合は除外しない）

    Returns:
        フィルタリングされたエントリーのリスト
    """
    if not entries:
        return entries

    results = []

    for entry in entries:
        entry_tags = entry.get('tags', [])

        # exclude_tags のチェック（優先）
        if exclude_tags:
            # 除外タグが1つでも含まれている場合はスキップ
            if any(tag in exclude_tags for tag in entry_tags):
                continue

        # include_tags のチェック
        if include_tags is not None:
            # 含めるタグが1つでも含まれている場合のみ追加
            if any(tag in include_tags for tag in entry_tags):
                results.append(entry)
        else:
            # include_tags が指定されていない場合は、除外されなかったエントリーを全て追加
            results.append(entry)

    return results
