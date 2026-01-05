# orgjournal-mcp

![Tests](https://github.com/u-yuta/orgjournal-mcp/workflows/Tests/badge.svg)

Org-mode journal files MCP server for LLM access.

## Overview

Read monthly Org-mode journal files and make them searchable from LLM (Claude, etc.).

## Features

### MCP Tools

1. **get_journal_entries** - Get journal entries by date range
2. **search_journal** - Search journal by keywords
3. **get_recent_entries** - Get recent N days entries (excludes "chore" tag by default)
4. **get_entries_by_tag** - Filter journal entries by tags (include/exclude)

## Installation

```bash
# Clone repository
git clone <repository-url>
cd orgjournal-mcp

# Install with uv
uv pip install -e .

# Or sync dependencies only
uv sync
```

## Usage

### Run as MCP Server

```bash
# Run as Python module
python -m orgjournal_mcp

# Or with uv run
uv run python -m orgjournal_mcp

# Or use installed command
orgjournal-mcp
```

### Claude Desktop Configuration

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "orgjournal": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/orgjournal-mcp",
        "run",
        "python",
        "-m",
        "orgjournal_mcp"
      ]
    }
  }
}
```

## Journal File Structure

Default structure:

- **Directory**: `~/Documents/org/p1-journal/`
- **Filename**: `journal-YYYY-MM.org` (e.g., `journal-2025-01.org`)
- **Entry Level**: Level 4 headings (`**** Entry Title`)
- **Timestamp**: Each entry has `[YYYY-MM-DD DAY HH:MM]` format timestamp

### Example Journal File

```org
* 2025
** 2025-01 January
*** 2025-01-04 Saturday
**** [2025-01-04 Sat 09:00] Project Meeting :meeting:work:
Discussed new features in today's project meeting.

**** [2025-01-04 Sat 14:30] Code Review Completed
Completed PR review and merged.
```

## Customization

To change default journal directory, edit `src/orgjournal_mcp/config.py`:

```python
DEFAULT_JOURNAL_DIR = Path.home() / "Documents" / "org" / "your-journal-dir"
```

## Tool Details

### get_journal_entries

Get journal entries for a specified date range.

**Parameters:**
- `last_days` (optional): Get entries from the last N days (e.g., 7, 30, 90)
- `since` (optional): Start date in YYYY-MM-DD format
- `before` (optional): End date in YYYY-MM-DD format
- `journal_dir` (optional): Custom journal directory path

**Returns:**
A dictionary containing:
- `entries`: List of journal entry objects
- `count`: Total number of entries
- `period`: Object with search period information (last_days, since, before)

**Entry Object Format:**
```json
{
  "title": "Entry Title",
  "timestamp": "2025-01-04T09:00:00",
  "tags": ["meeting", "work"],
  "body": "Entry content...",
  "file": "journal-2025-01.org"
}
```

**Examples:**
```python
# Get last 7 days entries
get_journal_entries(last_days=7)

# Get entries from January 1, 2025 onwards
get_journal_entries(since="2025-01-01")

# Get entries for January 2025
get_journal_entries(since="2025-01-01", before="2025-02-01")
```

### search_journal

Search journals by keyword with flexible search options.

**Parameters:**
- `query` (required): Search keyword or phrase
- `last_days` (optional): Search period (last N days)
- `since` (optional): Start date in YYYY-MM-DD format
- `before` (optional): End date in YYYY-MM-DD format
- `search_in_body` (optional, default: True): Include body in search
- `search_in_title` (optional, default: True): Include title in search
- `search_in_tags` (optional, default: True): Include tags in search
- `journal_dir` (optional): Custom journal directory path

**Returns:**
A dictionary containing:
- `entries`: List of matching journal entry objects
- `count`: Number of matching entries
- `query`: The search query used
- `search_options`: Object with search configuration (search_in_body, search_in_title, search_in_tags)

**Examples:**
```python
# Search for "meeting" in the last 30 days
search_journal("meeting", last_days=30)

# Search in tags only
search_journal("project", search_in_tags=True, search_in_body=False, search_in_title=False)

# Search with date range
search_journal("review", since="2025-01-01", before="2025-02-01")
```

### get_recent_entries

Get entries from the last N days. **By default, excludes entries with "chore" tag.**

**Parameters:**
- `days` (optional, default: 7): Number of days to retrieve
- `journal_dir` (optional): Custom journal directory path

**Examples:**
```python
# Get last 7 days entries (excluding "chore" tag)
get_recent_entries()

# Get last 30 days entries (excluding "chore" tag)
get_recent_entries(days=30)
```

### get_entries_by_tag

Filter journal entries by tags with include/exclude functionality.

**Parameters:**
- `tags` (optional): List of tags to include
- `exclude_tags` (optional, default: `None`): List of tags to exclude
- `last_days` (optional): Get entries from the last N days
- `since` (optional): Start date (YYYY-MM-DD)
- `before` (optional): End date (YYYY-MM-DD)
- `journal_dir` (optional): Custom journal directory path

**Examples:**
```python
# Get "work" tagged entries
get_entries_by_tag(tags=["work"], last_days=30)

# Exclude "meeting" and "review" tags
get_entries_by_tag(exclude_tags=["meeting", "review"], last_days=30)

# Exclude "chore" tag explicitly
get_entries_by_tag(exclude_tags=["chore"], last_days=30)

# Combine include and exclude
get_entries_by_tag(tags=["work"], exclude_tags=["chore", "meeting"])
```

## Development

```bash
# Setup dev environment
uv sync --all-groups

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome.
