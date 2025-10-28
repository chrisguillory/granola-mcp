# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an MCP (Model Context Protocol) server that provides access to Granola meeting notes and transcripts via Claude Code. The server uses Granola's private, undocumented API (discovered through reverse engineering) to enable AI assistants to search meetings, download notes, access transcripts, and manage meeting data.

**Important**: Granola's API is private and subject to change. The server uses strict Pydantic validation to fail fast when API changes occur.

## Architecture

### Core Components

**Main server** (`granola-mcp.py`):
- FastMCP server with async/await architecture
- Manages HTTP client (`httpx.AsyncClient`) and temp directory lifecycle via `lifespan` context manager
- All MCP tools defined as `@mcp.tool` decorated async functions
- Global state: `_http_client`, `_temp_dir`, `_export_dir`

**Data models** (`src/models.py`):
- Strict Pydantic models with `extra='forbid'` and `strict=True` - fail fast on API changes
- Hierarchy: `DocumentsResponse` → `GranolaDocument` → nested models for People, GoogleCalendarEvent, etc.
- Simplified response models: `MeetingListItem`, `NoteDownloadResult`, `TranscriptDownloadResult`

**Helper utilities** (`src/helpers.py`):
- `get_auth_token()`: Reads WorkOS OAuth token from `~/Library/Application Support/Granola/supabase.json`
- `prosemirror_to_markdown()`: Recursive converter for ProseMirror JSON → Markdown (handles nested lists, headings, links, formatting)
- `analyze_markdown_metadata()`: Extracts structural metrics (sections, bullets, word count)

**Logging utilities** (`src/logging.py`):
- `DualLogger`: Logs to both stdout and MCP client context for debugging

### API Endpoints Used

The server interacts with these Granola API endpoints:
- `POST https://api.granola.ai/v2/get-documents` - List/search meetings with pagination
- `POST https://api.granola.ai/v1/get-document-panels` - Get AI-generated notes (ProseMirror JSON)
- `POST https://api.granola.ai/v1/get-document-transcript` - Get meeting transcript segments
- `POST https://api.granola.ai/v1/get-documents-batch` - Batch fetch meetings by IDs
- `POST https://api.granola.ai/v1/get-document-lists-metadata` - Get meeting lists/collections
- `POST https://api.granola.ai/v1/update-document` - Update document fields (used for delete/undelete)

All requests require `Authorization: Bearer {access_token}` header.

### Key Design Patterns

**Authentication**: OAuth tokens read from local Granola app storage - no credential management needed

**Temp file management**: Downloads saved to `TemporaryDirectory` that auto-cleans on server shutdown

**ProseMirror conversion**: Recursive tree traversal with depth tracking for nested list indentation

**Strict validation**: Pydantic models catch API changes immediately rather than failing silently

**Dual logging**: All operations logged to both stdout (for debugging) and MCP context (for user visibility)

## Development Commands

### Formatting
```bash
uvx ruff format .
```

### Installation
```bash
# Add to Claude Code MCP config (user scope)
claude mcp add --scope user --transport stdio granola -- uv run --script ~/granola-mcp/granola-mcp.py
```

### Debugging
```bash
# Run with PyCharm remote debugging
uv run --script granola-mcp.py --debug --debug-host localhost --debug-port 5678
```

## Development Conventions

### Python Execution

Use `uv run` with heredoc for interactive Python execution:

```bash
uv run --no-project --with colorama python - <<'PY'
from colorama import Fore
print(Fore.GREEN + "Analysis result" + Fore.RESET)
PY

## Key Implementation Details

### ProseMirror to Markdown Conversion

The `prosemirror_to_markdown()` function handles recursive conversion with these node types:
- `doc`: Root node - joins children with double newlines
- `heading`: Uses `level` attr to determine `#` count
- `paragraph`, `bulletList`, `orderedList`: Handles nesting via `depth` parameter
- `listItem`: Processed by `process_list_item()` which handles nested lists with proper indentation
- Text marks: `bold` → `**text**`, `italic` → `*text*`, `link` → `[text](href)`, `code` → `` `text` ``

### Download Tools Architecture

All download tools follow this pattern:
1. Fetch document metadata from `/v2/get-documents` for title/date
2. Fetch specific content (panels for notes, transcript segments, etc.)
3. Convert to Markdown format matching Granola's official export format
4. Add title and date header
5. Calculate metadata (word count, sections, duration, etc.)
6. Write to temp file and return result with metadata

### Meeting Search vs. Batch Retrieval

- `search_meetings()`: Supports pagination, title filtering, list filtering - for discovery
- `get_meetings()`: Takes list of IDs and fetches in batch - for fetching specific meetings after discovery
- Pattern: Use `get_meeting_lists()` → `get_meetings(document_ids)` to fetch all meetings in a collection

### Delete/Undelete Implementation

Deletion is soft delete via timestamp:
- `delete_meeting()`: Sets `deleted_at` to current UTC timestamp
- `undelete_meeting()`: Sets `deleted_at` to `null`
- Deleted meetings appear in `deleted` array of API responses but not in regular searches
- `list_deleted_meetings()` returns IDs from the `deleted` array

## Code Style

- Single quotes for strings (enforced by Ruff)
- Async/await throughout
- Type hints on all function signatures
- Comprehensive docstrings with Args/Returns sections
- Pydantic models for all API responses
- Fail fast validation (no silent failures)

## Common Modifications

**Adding a new tool**: Follow the pattern in existing tools - add `@mcp.tool` decorator, use `DualLogger` for logging, validate responses with Pydantic models, return structured result models.

**Updating models**: When API changes, update Pydantic models in `src/models.py`. Strict validation will immediately catch mismatches.

**Adding API endpoint**: Add to helpers or main file, use `_http_client` for requests, add `get_auth_headers()` for authentication, validate response with new Pydantic model.
