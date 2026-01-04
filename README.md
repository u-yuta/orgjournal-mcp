# orgjournal-mcp

![Tests](https://github.com/u-yuta/orgjournal-mcp/workflows/Tests/badge.svg)

Org-mode journal files MCP server for LLM access.

## Overview

Read monthly Org-mode journal files and make them searchable from LLM (Claude, etc.).

## Features

### MCP Tools

1. **get_journal_entries** - Get journal entries by date range
2. **search_journal** - Search journal by keywords
3. **get_recent_entries** - Get recent N days entries

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

## Development

```bash
# Setup dev environment
uv sync --all-groups

# Run tests
uv run pytest
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome.
